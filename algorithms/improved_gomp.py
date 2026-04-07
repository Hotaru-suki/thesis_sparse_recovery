from __future__ import annotations

import math
import time

import numpy as np

from utils.linalg import IncrementalGramSolver, estimate_condition_number, solve_least_squares, topk_indices


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
    return_info: bool = True,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    Improved gOMP with engineering-side optimizations.

    Adaptive screening is inspired by the adaptive partial-selection direction
    in [15], but the rule here is an engineering design for this thesis project
    rather than a line-by-line reproduction.
    """
    m, n = Phi.shape
    if group_size <= 0 or min_group_size <= 0:
        raise ValueError("group_size and min_group_size must be positive")
    max_iter = max_iter or min(m, max(1, math.ceil((k or m) / max(group_size, 1))))
    tol = float(tol) if tol is not None else 1e-8

    residual = y.copy()
    previous_residual_norm = float(np.linalg.norm(residual))
    residual_history = [previous_residual_norm]
    support: list[int] = []
    support_history: list[list[int]] = []
    support_size_history: list[int] = []
    solver_time_history: list[float] = []
    candidate_size_history: list[int] = []
    group_size_history: list[int] = []
    x_hat = np.zeros(n, dtype=float)
    stop_reason = "max_iter"
    fallback_reason = ""
    solver_fallback_count = 0
    solver = IncrementalGramSolver(Phi=Phi, y=y) if use_incremental_solver else None
    duplicate_candidate_hits = 0
    support_condition_history: list[float] = []
    t0 = time.perf_counter()

    for iteration in range(1, max_iter + 1):
        residual_norm = float(np.linalg.norm(residual))
        correlations = np.abs(Phi.T @ residual)
        if support:
            correlations[np.asarray(support, dtype=int)] = -np.inf

        active_group_size = int(np.clip(math.ceil(group_size * residual_norm / max(np.linalg.norm(y), 1e-12)), min_group_size, group_size))
        remaining = n - len(support)
        active_group_size = min(active_group_size, remaining)
        if active_group_size <= 0:
            stop_reason = "support_exhausted"
            break

        pool_size = _adaptive_pool_size(
            correlations=np.where(np.isfinite(correlations), correlations, 0.0),
            residual_norm=residual_norm,
            previous_residual_norm=previous_residual_norm,
            screening_ratio=screening_ratio,
            base_group_size=active_group_size,
            remaining=remaining,
            iteration=iteration,
        )
        candidates = topk_indices(correlations, pool_size)
        scores = _debiased_scores(Phi=Phi, residual=residual, support=support, candidates=candidates)
        local_choice = topk_indices(scores, active_group_size)
        raw_chosen = [int(candidates[idx]) for idx in local_choice]
        duplicate_candidate_hits += sum(1 for idx in raw_chosen if idx in support)
        chosen = [idx for idx in raw_chosen if idx not in support]
        if not chosen:
            stop_reason = "empty_candidate_set"
            break

        if solver is not None:
            solver.extend(chosen)
            solve_t0 = time.perf_counter()
            coef, solver_name = solver.solve()
            solver_time_history.append(time.perf_counter() - solve_t0)
            current_support = solver.support.copy()
        else:
            current_support = support + chosen
            solve_t0 = time.perf_counter()
            coef, solver_name = solve_least_squares(Phi[:, current_support], y)
            solver_time_history.append(time.perf_counter() - solve_t0)

        if solver_name not in {"gram_solve", "lstsq"}:
            fallback_reason = solver_name
            solver_fallback_count += 1

        support = current_support
        x_hat[:] = 0.0
        x_hat[np.asarray(support, dtype=int)] = coef
        support_condition_history.append(estimate_condition_number(Phi[:, support]))
        residual = y - Phi @ x_hat
        new_residual_norm = float(np.linalg.norm(residual))
        drop_ratio = (previous_residual_norm - new_residual_norm) / max(previous_residual_norm, 1e-12)

        residual_history.append(new_residual_norm)
        support_history.append(sorted(support.copy()))
        support_size_history.append(len(support))
        candidate_size_history.append(pool_size)
        group_size_history.append(len(chosen))

        if new_residual_norm <= tol:
            stop_reason = "residual_tol"
            break
        if k is not None and len(support) >= k:
            stop_reason = "target_sparsity_reached"
            break
        if use_noise_aware_stop and noise_sigma is not None and new_residual_norm**2 <= 1.2 * m * (noise_sigma**2):
            stop_reason = "noise_floor"
            break
        if use_noise_aware_stop and len(residual_history) >= 3:
            recent_improvement = residual_history[-2] - residual_history[-1]
            previous_improvement = residual_history[-3] - residual_history[-2]
            if recent_improvement <= min_residual_drop * max(residual_history[-2], 1e-12) and previous_improvement <= min_residual_drop * max(residual_history[-3], 1e-12):
                stop_reason = "small_residual_drop"
                break

        previous_residual_norm = new_residual_norm

    info = {
        "iterations": len(support_history),
        "runtime_sec": time.perf_counter() - t0,
        "residual_history": residual_history,
        "support_history": support_history,
        "support_size_history": support_size_history,
        "stop_reason": stop_reason,
        "fallback_reason": fallback_reason,
        "solver_fallback_count": solver_fallback_count,
        "duplicate_candidate_hits": duplicate_candidate_hits,
        "solver_time_history": solver_time_history,
        "used_incremental_solver": use_incremental_solver,
        "candidate_size_history": candidate_size_history,
        "group_size_history": group_size_history,
        "screening_pool_size_avg": float(np.mean(candidate_size_history)) if candidate_size_history else 0.0,
        "support_condition_history": support_condition_history,
        "max_support_condition": float(max(support_condition_history)) if support_condition_history else 0.0,
    }
    return x_hat, np.asarray(sorted(support), dtype=int), info if return_info else {}
