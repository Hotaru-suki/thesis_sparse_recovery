from __future__ import annotations

import math
import time
from dataclasses import dataclass, field

import numpy as np

from utils.linalg import IncrementalCholeskySolver, IncrementalGramSolver, estimate_condition_number, solve_least_squares, topk_indices


SolverType = IncrementalGramSolver | IncrementalCholeskySolver


@dataclass(frozen=True)
class ImprovedGompOptions:
    group_size: int = 2
    k: int | None = None
    tol: float | None = None
    max_iter: int | None = None
    screening_ratio: float = 3.0
    min_group_size: int = 1
    use_noise_aware_stop: bool = True
    use_incremental_solver: bool = True
    noise_sigma: float | None = None
    min_residual_drop: float = 1e-4
    use_tail_refinement: bool = False
    use_gain_reranking: bool = False
    use_forward_backward: bool = False
    use_two_phase_tail: bool = False
    use_cholesky_solver: bool = True
    return_info: bool = True


@dataclass
class ImprovedGompState:
    residual: np.ndarray
    previous_residual_norm: float
    initial_residual_norm: float
    x_hat: np.ndarray
    support: list[int] = field(default_factory=list)
    residual_history: list[float] = field(default_factory=list)
    support_history: list[list[int]] = field(default_factory=list)
    support_size_history: list[int] = field(default_factory=list)
    solver_time_history: list[float] = field(default_factory=list)
    candidate_size_history: list[int] = field(default_factory=list)
    group_size_history: list[int] = field(default_factory=list)
    support_condition_history: list[float] = field(default_factory=list)
    stop_reason: str = "max_iter"
    fallback_reason: str = ""
    solver_fallback_count: int = 0
    duplicate_candidate_hits: int = 0
    rescue_attempted: bool = False
    rescue_accepted: bool = False
    soft_stop_count: int = 0


def _build_options(**kwargs: object) -> ImprovedGompOptions:
    return ImprovedGompOptions(**kwargs)


def _build_solver(*, Phi: np.ndarray, y: np.ndarray, options: ImprovedGompOptions) -> SolverType | None:
    if not options.use_incremental_solver:
        return None
    if options.use_cholesky_solver:
        return IncrementalCholeskySolver(Phi=Phi, y=y)
    return IncrementalGramSolver(Phi=Phi, y=y)


def _init_state(*, y: np.ndarray, n: int) -> ImprovedGompState:
    residual = y.copy()
    residual_norm = float(np.linalg.norm(residual))
    return ImprovedGompState(
        residual=residual,
        previous_residual_norm=residual_norm,
        initial_residual_norm=residual_norm,
        x_hat=np.zeros(n, dtype=float),
        residual_history=[residual_norm],
    )


def _note_solver_status(state: ImprovedGompState, solver_name: str) -> None:
    if solver_name not in {"gram_solve", "lstsq", "cholesky_solve"}:
        state.fallback_reason = solver_name
        state.solver_fallback_count += 1


def _record_iteration(
    *,
    state: ImprovedGompState,
    Phi: np.ndarray,
    support: list[int],
    residual_norm: float,
    pool_size: int,
    chosen_size: int,
) -> None:
    state.residual_history.append(residual_norm)
    state.support_history.append(sorted(support.copy()))
    state.support_size_history.append(len(support))
    state.candidate_size_history.append(pool_size)
    state.group_size_history.append(chosen_size)
    state.support_condition_history.append(estimate_condition_number(Phi[:, support]))


def _sync_state_after_support_update(
    *,
    state: ImprovedGompState,
    support: list[int],
    x_hat: np.ndarray,
    residual: np.ndarray,
) -> None:
    state.support = support
    state.x_hat = x_hat
    state.residual = residual


def _adaptive_pool_size(
    correlations: np.ndarray,
    residual_norm: float,
    previous_residual_norm: float,
    screening_ratio: float,
    base_group_size: int,
    remaining: int,
    iteration: int,
) -> int:
    if remaining <= 0:
        return 0
    sorted_corr = np.sort(correlations)[::-1]
    head = sorted_corr[: min(5, sorted_corr.size)]
    decay = 1.0
    if head.size >= 2 and abs(head[0]) > 1e-12:
        decay = float(np.clip(head[0] / max(head[-1], 1e-12), 1.0, 4.0))
    improvement = max(previous_residual_norm - residual_norm, 0.0) / max(previous_residual_norm, 1e-12)
    dynamic = screening_ratio + 0.8 * decay + 2.0 * (1.0 - improvement) + 0.15 * iteration
    size = int(math.ceil(base_group_size * dynamic))
    return int(np.clip(size, base_group_size, remaining))


def _adaptive_group_size(
    *,
    base_group_size: int,
    min_group_size: int,
    residual_norm: float,
    initial_residual_norm: float,
    previous_drop_ratio: float,
    remaining: int,
    remaining_target: int | None,
) -> int:
    if remaining <= 0:
        return 0
    size = base_group_size
    residual_ratio = residual_norm / max(initial_residual_norm, 1e-12)
    if residual_ratio < 0.35:
        size = max(size - 1, min_group_size)
    if previous_drop_ratio < 0.03:
        size = min(size + 1, base_group_size + 1)
    if previous_drop_ratio > 0.2:
        size = max(size - 1, min_group_size)
    if remaining_target is not None:
        size = min(size, remaining_target)
    return int(np.clip(size, min_group_size, remaining))


def _debiased_scores(
    Phi: np.ndarray,
    residual: np.ndarray,
    support: list[int],
    candidates: np.ndarray,
) -> np.ndarray:
    if candidates.size == 0:
        return np.zeros(0, dtype=float)
    if not support:
        return np.abs(Phi[:, candidates].T @ residual)

    basis = Phi[:, support]
    q_factor, _ = np.linalg.qr(basis, mode="reduced")
    scores = np.empty(candidates.size, dtype=float)
    for i, idx in enumerate(candidates):
        atom = Phi[:, int(idx)]
        ortho = atom - q_factor @ (q_factor.T @ atom)
        denom = max(float(np.linalg.norm(ortho)), 1e-12)
        scores[i] = abs(float(ortho @ residual)) / denom
    return scores


def _candidate_priority(
    Phi: np.ndarray,
    residual: np.ndarray,
    support: list[int],
    candidates: np.ndarray,
    *,
    debias_weight: float = 0.35,
) -> np.ndarray:
    raw_scores = np.abs(Phi[:, candidates].T @ residual) if candidates.size else np.zeros(0, dtype=float)
    if candidates.size == 0:
        return raw_scores
    debiased = _debiased_scores(Phi=Phi, residual=residual, support=support, candidates=candidates)
    if not np.any(np.isfinite(debiased)):
        return raw_scores
    raw_scale = max(float(np.max(raw_scores)), 1e-12)
    debiased_scale = max(float(np.max(np.abs(debiased))), 1e-12)
    return raw_scores / raw_scale + debias_weight * debiased / debiased_scale


def _approx_gain_priority(
    *,
    Phi: np.ndarray,
    y: np.ndarray,
    residual: np.ndarray,
    support: list[int],
    candidates: np.ndarray,
    shortlist_size: int,
    debias_weight: float = 0.35,
    gain_weight: float = 0.25,
) -> np.ndarray:
    base_priority = _candidate_priority(Phi=Phi, residual=residual, support=support, candidates=candidates, debias_weight=debias_weight)
    if candidates.size == 0:
        return base_priority
    shortlist_size = min(shortlist_size, candidates.size)
    shortlist_idx = topk_indices(base_priority, shortlist_size)
    shortlist = candidates[shortlist_idx]
    gain_scores = _residual_gain_scores(Phi=Phi, y=y, support=support, candidates=shortlist)
    gain_scale = max(float(np.max(np.abs(gain_scores))), 1e-12)
    combined = base_priority.copy()
    combined[shortlist_idx] += gain_weight * gain_scores / gain_scale
    return combined


def _solve_support(
    *,
    Phi: np.ndarray,
    y: np.ndarray,
    support: list[int],
    solver: SolverType | None,
    solver_time_history: list[float],
) -> tuple[np.ndarray, list[int], str]:
    solve_t0 = time.perf_counter()
    if solver is not None:
        coef, solver_name = solver.solve()
        solver_time_history.append(time.perf_counter() - solve_t0)
        return coef, solver.support.copy(), solver_name
    coef, solver_name = solve_least_squares(Phi[:, support], y)
    solver_time_history.append(time.perf_counter() - solve_t0)
    return coef, support.copy(), solver_name


def _residual_gain_scores(
    *,
    Phi: np.ndarray,
    y: np.ndarray,
    support: list[int],
    candidates: np.ndarray,
) -> np.ndarray:
    if candidates.size == 0:
        return np.zeros(0, dtype=float)
    scores = np.zeros(candidates.size, dtype=float)
    base_support = support.copy()
    for i, candidate in enumerate(candidates):
        trial_support = base_support + [int(candidate)]
        coef, _ = solve_least_squares(Phi[:, trial_support], y)
        trial_x = np.zeros(Phi.shape[1], dtype=float)
        trial_x[np.asarray(trial_support, dtype=int)] = coef
        scores[i] = -float(np.linalg.norm(y - Phi @ trial_x))
    return scores


def _try_rescue_step(
    *,
    Phi: np.ndarray,
    y: np.ndarray,
    residual: np.ndarray,
    support: list[int],
    residual_norm: float,
    group_size: int,
    screening_ratio: float,
    min_group_size: int,
    k: int | None,
    solver: SolverType | None,
    solver_time_history: list[float],
) -> tuple[list[int], np.ndarray, np.ndarray, float, str]:
    remaining = Phi.shape[1] - len(support)
    if remaining <= 0:
        return support, np.zeros(Phi.shape[1], dtype=float), residual, residual_norm, "support_exhausted"
    if k is not None and len(support) >= k:
        return support, np.zeros(Phi.shape[1], dtype=float), residual, residual_norm, "target_sparsity_reached"

    remaining_target = None if k is None else max(k - len(support), 0)
    if remaining_target is not None and remaining_target <= 2:
        rescue_budget = 1
    else:
        rescue_budget = max(min_group_size + 1, group_size)
    if remaining_target is not None:
        rescue_budget = min(rescue_budget, remaining_target)
    rescue_budget = min(rescue_budget, remaining)
    if rescue_budget <= 0:
        return support, np.zeros(Phi.shape[1], dtype=float), residual, residual_norm, "empty_candidate_set"

    correlations = np.abs(Phi.T @ residual)
    if support:
        correlations[np.asarray(support, dtype=int)] = -np.inf
    pool_size = min(
        remaining,
        max(rescue_budget, int(math.ceil(screening_ratio * max(group_size, 1) + rescue_budget))),
    )
    candidates = topk_indices(correlations, pool_size)
    priority = _candidate_priority(Phi=Phi, residual=residual, support=support, candidates=candidates, debias_weight=0.2)
    rescue_choice = [int(candidates[idx]) for idx in topk_indices(priority, rescue_budget)]
    rescue_choice = [idx for idx in rescue_choice if idx not in support]
    if not rescue_choice:
        return support, np.zeros(Phi.shape[1], dtype=float), residual, residual_norm, "empty_candidate_set"

    solver_state = solver.snapshot() if solver is not None else None
    if solver is not None:
        solver.extend(rescue_choice)
        coef, updated_support, solver_name = _solve_support(
            Phi=Phi,
            y=y,
            support=solver.support,
            solver=solver,
            solver_time_history=solver_time_history,
        )
    else:
        updated_support = support + rescue_choice
        coef, updated_support, solver_name = _solve_support(
            Phi=Phi,
            y=y,
            support=updated_support,
            solver=None,
            solver_time_history=solver_time_history,
        )

    x_hat = np.zeros(Phi.shape[1], dtype=float)
    x_hat[np.asarray(updated_support, dtype=int)] = coef
    new_residual = y - Phi @ x_hat
    new_residual_norm = float(np.linalg.norm(new_residual))
    if solver is not None and solver_state is not None:
        solver.restore(solver_state)
    return updated_support, x_hat, new_residual, new_residual_norm, solver_name


def _should_attempt_rescue(
    *,
    iteration: int,
    k: int | None,
    support_size: int,
    active_group_size: int,
    min_group_size: int,
    residual_norm: float,
    initial_residual_norm: float,
    drop_ratio: float,
    rescue_attempted: bool,
) -> bool:
    if rescue_attempted or k is None or support_size >= k:
        return False
    remaining_target = k - support_size
    if remaining_target <= 0:
        return False
    if iteration < 2:
        return False
    residual_ratio = residual_norm / max(initial_residual_norm, 1e-12)
    conservative_signature = active_group_size <= min_group_size and drop_ratio < 0.01 and residual_ratio < 0.35
    stalled_signature = active_group_size <= min_group_size and remaining_target <= 2 and residual_ratio < 0.45
    near_target_signature = remaining_target <= 2 and residual_ratio < 0.4
    return conservative_signature or stalled_signature or near_target_signature


def _phase_group_size(
    *,
    active_group_size: int,
    remaining_target: int | None,
    use_two_phase_tail: bool,
) -> int:
    if not use_two_phase_tail or remaining_target is None:
        return active_group_size
    if remaining_target <= 2:
        return 1
    if remaining_target <= 4:
        return min(active_group_size, 2)
    return active_group_size


def _select_candidates(
    *,
    Phi: np.ndarray,
    y: np.ndarray,
    residual: np.ndarray,
    support: list[int],
    candidates: np.ndarray,
    active_group_size: int,
    use_tail_refinement: bool,
    remaining_target: int | None,
    use_gain_reranking: bool,
) -> list[int]:
    if use_gain_reranking:
        priority = _approx_gain_priority(
            Phi=Phi,
            y=y,
            residual=residual,
            support=support,
            candidates=candidates,
            shortlist_size=max(active_group_size + 2, 5),
        )
    else:
        priority = _candidate_priority(Phi=Phi, residual=residual, support=support, candidates=candidates)
    if candidates.size == 0 or active_group_size <= 0:
        return []

    local_choice = topk_indices(priority, active_group_size)
    raw_chosen = [int(candidates[idx]) for idx in local_choice]

    near_tail = remaining_target is not None and remaining_target <= max(2, active_group_size)
    if not use_tail_refinement or not near_tail:
        return raw_chosen

    shortlist_size = min(candidates.size, max(active_group_size + 2, 4))
    shortlist = candidates[topk_indices(priority, shortlist_size)]
    gain_scores = _residual_gain_scores(Phi=Phi, y=y, support=support, candidates=shortlist)
    refined_choice = topk_indices(gain_scores, active_group_size)
    return [int(shortlist[idx]) for idx in refined_choice]


def _try_tail_swap(
    *,
    Phi: np.ndarray,
    y: np.ndarray,
    support: list[int],
    x_hat: np.ndarray,
    residual_norm: float,
    candidates: np.ndarray,
    max_swaps: int = 1,
) -> tuple[list[int], np.ndarray, float, bool]:
    if not support or candidates.size == 0 or max_swaps <= 0:
        return support, x_hat, residual_norm, False

    support_array = np.asarray(support, dtype=int)
    support_coef = np.abs(x_hat[support_array])
    drop_order = support_array[np.argsort(support_coef)]
    best_support = support.copy()
    best_x_hat = x_hat.copy()
    best_residual_norm = residual_norm
    improved = False

    for drop_idx in drop_order[:max_swaps]:
        reduced_support = [idx for idx in support if idx != int(drop_idx)]
        for candidate in candidates:
            candidate = int(candidate)
            if candidate in reduced_support:
                continue
            trial_support = reduced_support + [candidate]
            coef, _ = solve_least_squares(Phi[:, trial_support], y)
            trial_x = np.zeros(Phi.shape[1], dtype=float)
            trial_x[np.asarray(trial_support, dtype=int)] = coef
            trial_residual_norm = float(np.linalg.norm(y - Phi @ trial_x))
            if trial_residual_norm + 1e-12 < best_residual_norm:
                best_support = trial_support
                best_x_hat = trial_x
                best_residual_norm = trial_residual_norm
                improved = True
    return best_support, best_x_hat, best_residual_norm, improved


def _maybe_apply_forward_backward(
    *,
    Phi: np.ndarray,
    y: np.ndarray,
    state: ImprovedGompState,
    solver: SolverType | None,
    options: ImprovedGompOptions,
    remaining_target: int | None,
    candidates: np.ndarray,
    new_residual_norm: float,
) -> tuple[SolverType | None, float]:
    if not options.use_forward_backward or remaining_target is None or remaining_target > 1 or len(state.support) < 2:
        return solver, new_residual_norm

    swap_priority = _candidate_priority(
        Phi=Phi,
        residual=state.residual,
        support=state.support,
        candidates=candidates,
        debias_weight=0.2,
    )
    swap_shortlist_size = min(candidates.size, 3)
    swap_candidates = candidates[topk_indices(swap_priority, swap_shortlist_size)]
    swapped_support, swapped_x_hat, swapped_residual_norm, swapped = _try_tail_swap(
        Phi=Phi,
        y=y,
        support=state.support,
        x_hat=state.x_hat,
        residual_norm=new_residual_norm,
        candidates=swap_candidates,
        max_swaps=1,
    )
    swap_gain = (new_residual_norm - swapped_residual_norm) / max(new_residual_norm, 1e-12)
    if not swapped or swap_gain < 5e-3:
        return solver, new_residual_norm

    swapped_residual = y - Phi @ swapped_x_hat
    _sync_state_after_support_update(
        state=state,
        support=swapped_support,
        x_hat=swapped_x_hat,
        residual=swapped_residual,
    )
    solver = _build_solver(Phi=Phi, y=y, options=options)
    if solver is not None:
        solver.extend(state.support)
    return solver, swapped_residual_norm


def _accept_rescue(
    *,
    state: ImprovedGompState,
    Phi: np.ndarray,
    support: list[int],
    x_hat: np.ndarray,
    residual: np.ndarray,
    residual_norm: float,
    support_gain: int,
) -> None:
    _sync_state_after_support_update(
        state=state,
        support=support,
        x_hat=x_hat,
        residual=residual,
    )
    state.residual_history[-1] = residual_norm
    state.support_history[-1] = sorted(support.copy())
    state.support_size_history[-1] = len(support)
    state.group_size_history[-1] += support_gain
    state.support_condition_history[-1] = estimate_condition_number(Phi[:, support])
    state.rescue_accepted = True
    state.soft_stop_count = 0


def _finalize_info(
    *,
    state: ImprovedGompState,
    options: ImprovedGompOptions,
    runtime_sec: float,
) -> dict:
    return {
        "iterations": len(state.support_history),
        "runtime_sec": runtime_sec,
        "residual_history": state.residual_history,
        "support_history": state.support_history,
        "support_size_history": state.support_size_history,
        "stop_reason": state.stop_reason,
        "fallback_reason": state.fallback_reason,
        "solver_fallback_count": state.solver_fallback_count,
        "duplicate_candidate_hits": state.duplicate_candidate_hits,
        "solver_time_history": state.solver_time_history,
        "used_incremental_solver": options.use_incremental_solver,
        "candidate_size_history": state.candidate_size_history,
        "group_size_history": state.group_size_history,
        "screening_pool_size_avg": float(np.mean(state.candidate_size_history)) if state.candidate_size_history else 0.0,
        "support_condition_history": state.support_condition_history,
        "max_support_condition": float(max(state.support_condition_history)) if state.support_condition_history else 0.0,
        "rescue_attempted": state.rescue_attempted,
        "rescue_accepted": state.rescue_accepted,
        "soft_stop_count": state.soft_stop_count,
        "used_tail_refinement": options.use_tail_refinement,
        "used_gain_reranking": options.use_gain_reranking,
        "used_forward_backward": options.use_forward_backward,
        "used_two_phase_tail": options.use_two_phase_tail,
        "used_cholesky_solver": options.use_cholesky_solver,
    }


def improved_gomp(
    Phi: np.ndarray,
    y: np.ndarray,
    group_size: int = 2,
    k: int | None = None,
    tol: float | None = None,
    max_iter: int | None = None,
    screening_ratio: float = 3.0,
    min_group_size: int = 1,
    use_noise_aware_stop: bool = True,
    use_incremental_solver: bool = True,
    noise_sigma: float | None = None,
    min_residual_drop: float = 1e-4,
    use_tail_refinement: bool = False,
    use_gain_reranking: bool = False,
    use_forward_backward: bool = False,
    use_two_phase_tail: bool = False,
    use_cholesky_solver: bool = True,
    return_info: bool = True,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    Improved gOMP with engineering-side optimizations.

    Adaptive screening is inspired by the adaptive partial-selection direction
    in [15], but the rule here is an engineering design for this thesis project
    rather than a line-by-line reproduction.
    """
    options = _build_options(
        group_size=group_size,
        k=k,
        tol=tol,
        max_iter=max_iter,
        screening_ratio=screening_ratio,
        min_group_size=min_group_size,
        use_noise_aware_stop=use_noise_aware_stop,
        use_incremental_solver=use_incremental_solver,
        noise_sigma=noise_sigma,
        min_residual_drop=min_residual_drop,
        use_tail_refinement=use_tail_refinement,
        use_gain_reranking=use_gain_reranking,
        use_forward_backward=use_forward_backward,
        use_two_phase_tail=use_two_phase_tail,
        use_cholesky_solver=use_cholesky_solver,
        return_info=return_info,
    )

    m, n = Phi.shape
    if options.group_size <= 0 or options.min_group_size <= 0:
        raise ValueError("group_size and min_group_size must be positive")
    max_iter = options.max_iter or min(m, max(1, math.ceil(((options.k or m) / max(options.group_size, 1)))))
    tol = float(options.tol) if options.tol is not None else 1e-8

    state = _init_state(y=y, n=n)
    solver = _build_solver(Phi=Phi, y=y, options=options)
    t0 = time.perf_counter()

    for iteration in range(1, max_iter + 1):
        residual_norm = float(np.linalg.norm(state.residual))
        correlations = np.abs(Phi.T @ state.residual)
        if state.support:
            correlations[np.asarray(state.support, dtype=int)] = -np.inf

        remaining = n - len(state.support)
        remaining_target = None if options.k is None else max(options.k - len(state.support), 0)
        active_group_size = _adaptive_group_size(
            base_group_size=options.group_size,
            min_group_size=options.min_group_size,
            residual_norm=residual_norm,
            initial_residual_norm=state.initial_residual_norm,
            previous_drop_ratio=max(state.previous_residual_norm - residual_norm, 0.0) / max(state.previous_residual_norm, 1e-12),
            remaining=remaining,
            remaining_target=remaining_target,
        )
        active_group_size = _phase_group_size(
            active_group_size=active_group_size,
            remaining_target=remaining_target,
            use_two_phase_tail=options.use_two_phase_tail,
        )
        active_group_size = min(active_group_size, remaining)
        if active_group_size <= 0:
            state.stop_reason = "target_sparsity_reached" if remaining_target == 0 else "support_exhausted"
            break

        pool_size = _adaptive_pool_size(
            correlations=np.where(np.isfinite(correlations), correlations, 0.0),
            residual_norm=residual_norm,
            previous_residual_norm=state.previous_residual_norm,
            screening_ratio=options.screening_ratio,
            base_group_size=active_group_size,
            remaining=remaining,
            iteration=iteration,
        )
        candidates = topk_indices(correlations, pool_size)
        raw_chosen = _select_candidates(
            Phi=Phi,
            y=y,
            residual=state.residual,
            support=state.support,
            candidates=candidates,
            active_group_size=active_group_size,
            use_tail_refinement=options.use_tail_refinement,
            remaining_target=remaining_target,
            use_gain_reranking=options.use_gain_reranking,
        )
        state.duplicate_candidate_hits += sum(1 for idx in raw_chosen if idx in state.support)
        chosen = [idx for idx in raw_chosen if idx not in state.support]
        if not chosen:
            state.stop_reason = "empty_candidate_set"
            break

        if solver is not None:
            solver.extend(chosen)
            coef, current_support, solver_name = _solve_support(
                Phi=Phi,
                y=y,
                support=solver.support,
                solver=solver,
                solver_time_history=state.solver_time_history,
            )
        else:
            current_support = state.support + chosen
            coef, current_support, solver_name = _solve_support(
                Phi=Phi,
                y=y,
                support=current_support,
                solver=None,
                solver_time_history=state.solver_time_history,
            )
        _note_solver_status(state, solver_name)

        x_hat = np.zeros(n, dtype=float)
        x_hat[np.asarray(current_support, dtype=int)] = coef
        residual = y - Phi @ x_hat
        new_residual_norm = float(np.linalg.norm(residual))
        _sync_state_after_support_update(
            state=state,
            support=current_support,
            x_hat=x_hat,
            residual=residual,
        )

        solver, new_residual_norm = _maybe_apply_forward_backward(
            Phi=Phi,
            y=y,
            state=state,
            solver=solver,
            options=options,
            remaining_target=remaining_target,
            candidates=candidates,
            new_residual_norm=new_residual_norm,
        )
        drop_ratio = (state.previous_residual_norm - new_residual_norm) / max(state.previous_residual_norm, 1e-12)
        _record_iteration(
            state=state,
            Phi=Phi,
            support=state.support,
            residual_norm=new_residual_norm,
            pool_size=pool_size,
            chosen_size=len(chosen),
        )

        if _should_attempt_rescue(
            iteration=iteration,
            k=options.k,
            support_size=len(state.support),
            active_group_size=active_group_size,
            min_group_size=options.min_group_size,
            residual_norm=new_residual_norm,
            initial_residual_norm=state.initial_residual_norm,
            drop_ratio=drop_ratio,
            rescue_attempted=state.rescue_attempted,
        ):
            state.rescue_attempted = True
            rescued_support, rescued_x_hat, rescued_residual, rescued_residual_norm, rescue_solver_name = _try_rescue_step(
                Phi=Phi,
                y=y,
                residual=state.residual,
                support=state.support,
                residual_norm=new_residual_norm,
                group_size=options.group_size,
                screening_ratio=options.screening_ratio,
                min_group_size=options.min_group_size,
                k=options.k,
                solver=solver,
                solver_time_history=state.solver_time_history,
            )
            _note_solver_status(state, rescue_solver_name)
            rescue_gain = (new_residual_norm - rescued_residual_norm) / max(new_residual_norm, 1e-12)
            support_gain = len(rescued_support) - len(state.support)
            if support_gain > 0 and rescue_gain >= 2e-3:
                if solver is not None:
                    solver.extend([idx for idx in rescued_support if idx not in solver.support])
                _accept_rescue(
                    state=state,
                    Phi=Phi,
                    support=rescued_support,
                    x_hat=rescued_x_hat,
                    residual=rescued_residual,
                    residual_norm=rescued_residual_norm,
                    support_gain=support_gain,
                )
                new_residual_norm = rescued_residual_norm

        if new_residual_norm <= tol:
            state.stop_reason = "residual_tol"
            break
        if options.k is not None and len(state.support) >= options.k:
            state.stop_reason = "target_sparsity_reached"
            break
        if options.use_noise_aware_stop and options.noise_sigma is not None and new_residual_norm**2 <= 1.2 * m * (options.noise_sigma**2):
            state.stop_reason = "noise_floor"
            break
        if options.use_noise_aware_stop and len(state.residual_history) >= 3:
            recent_improvement = state.residual_history[-2] - state.residual_history[-1]
            previous_improvement = state.residual_history[-3] - state.residual_history[-2]
            low_recent_gain = recent_improvement <= options.min_residual_drop * max(state.residual_history[-2], 1e-12)
            low_previous_gain = previous_improvement <= options.min_residual_drop * max(state.residual_history[-3], 1e-12)
            state.soft_stop_count = state.soft_stop_count + 1 if low_recent_gain and low_previous_gain else 0
            if state.soft_stop_count >= 2:
                can_rescue = not state.rescue_attempted and (options.k is None or len(state.support) < options.k)
                if can_rescue:
                    state.rescue_attempted = True
                    rescued_support, rescued_x_hat, rescued_residual, rescued_residual_norm, rescue_solver_name = _try_rescue_step(
                        Phi=Phi,
                        y=y,
                        residual=state.residual,
                        support=state.support,
                        residual_norm=new_residual_norm,
                        group_size=options.group_size,
                        screening_ratio=options.screening_ratio,
                        min_group_size=options.min_group_size,
                        k=options.k,
                        solver=solver,
                        solver_time_history=state.solver_time_history,
                    )
                    _note_solver_status(state, rescue_solver_name)
                    rescue_gain = (new_residual_norm - rescued_residual_norm) / max(new_residual_norm, 1e-12)
                    if rescue_gain > max(5.0 * options.min_residual_drop, 1e-3):
                        if solver is not None:
                            solver.extend([idx for idx in rescued_support if idx not in solver.support])
                        _accept_rescue(
                            state=state,
                            Phi=Phi,
                            support=rescued_support,
                            x_hat=rescued_x_hat,
                            residual=rescued_residual,
                            residual_norm=rescued_residual_norm,
                            support_gain=len(rescued_support) - len(current_support),
                        )
                    else:
                        state.stop_reason = "small_residual_drop"
                        break
                else:
                    state.stop_reason = "small_residual_drop"
                    break
        state.previous_residual_norm = new_residual_norm

    info = _finalize_info(state=state, options=options, runtime_sec=time.perf_counter() - t0)
    return state.x_hat, np.asarray(sorted(state.support), dtype=int), info if return_info else {}
