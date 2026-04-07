from __future__ import annotations

import time

import numpy as np

from utils.linalg import (
    PhaseTimer,
    estimate_condition_number,
    init_phase_timing,
    stable_solve_gram,
    solve_least_squares,
    topk_indices,
)
from utils.memory import build_memory_breakdown


def _build_info(
    *,
    group_size: int,
    support_history: list[list[int]],
    residual_history: list[float],
    support_size: int,
    iteration_count: int,
    support_condition_history: list[float],
    stop_reason: str,
    fallback_reason: str,
    solver_fallback_count: int,
    duplicate_candidate_hits: int,
    runtime_sec: float,
    implementation: str,
    used_incremental_solver: bool,
    profile_level: str,
    phase_timings: dict[str, float],
    memory_breakdown: dict[str, int],
) -> dict:
    return {
        "iterations": iteration_count,
        "runtime_sec": runtime_sec,
        "residual_history": residual_history,
        "support_history": support_history,
        "support_size_history": [len(s) for s in support_history] if support_history else ([support_size] if support_size else []),
        "stop_reason": stop_reason,
        "fallback_reason": fallback_reason,
        "solver_fallback_count": solver_fallback_count,
        "duplicate_candidate_hits": duplicate_candidate_hits,
        "solver_time_history": [phase_timings.get("solve", 0.0)],
        "used_incremental_solver": used_incremental_solver,
        "profile_level": profile_level,
        "screening_pool_size_avg": float(group_size),
        "support_condition_history": support_condition_history,
        "max_support_condition": float(max(support_condition_history)) if support_condition_history else 0.0,
        "implementation": implementation,
        "timing_breakdown_sec": dict(phase_timings),
        "memory_breakdown_bytes": dict(memory_breakdown),
        "peak_working_set_bytes": int(memory_breakdown.get("peak_working_set_bytes", 0)),
    }


def _select_group(
    corr: np.ndarray,
    support_mask: np.ndarray,
    group_size: int,
    k: int | None,
    current_support_size: int,
) -> tuple[list[int], str | None, int]:
    remaining_support_budget = int(np.count_nonzero(~support_mask))
    if k is not None:
        remaining_support_budget = min(remaining_support_budget, max(k - current_support_size, 0))
    if remaining_support_budget <= 0:
        return [], "target_sparsity_reached" if k is not None and current_support_size >= k else "support_exhausted", 0
    raw_chosen = [int(idx) for idx in topk_indices(corr, min(group_size, remaining_support_budget))]
    chosen = [idx for idx in raw_chosen if not support_mask[idx]]
    duplicate_hits = len(raw_chosen) - len(chosen)
    if not chosen:
        return [], "empty_candidate_set", duplicate_hits
    return chosen, None, duplicate_hits


def _gomp_baseline(
    Phi: np.ndarray,
    y: np.ndarray,
    group_size: int,
    k: int | None,
    tol: float,
    max_iter: int,
    profile_level: str,
) -> tuple[np.ndarray, np.ndarray, dict]:
    _, n = Phi.shape
    residual = y.copy()
    x_hat = np.zeros(n, dtype=float)
    support: list[int] = []
    support_mask = np.zeros(n, dtype=bool)
    residual_history = [float(np.linalg.norm(residual))]
    support_history: list[list[int]] = []
    stop_reason = "max_iter"
    fallback_reason = ""
    solver_fallback_count = 0
    duplicate_candidate_hits = 0
    support_condition_history: list[float] = []
    phase_timings = init_phase_timing()
    t0 = time.perf_counter()

    for _ in range(max_iter):
        with PhaseTimer(phase_timings, "correlation"):
            corr = np.abs(Phi.T @ residual)
            corr[support_mask] = -np.inf
        with PhaseTimer(phase_timings, "selection"):
            chosen, stop_override, duplicate_hits = _select_group(corr, support_mask, group_size, k, len(support))
        duplicate_candidate_hits += duplicate_hits
        if stop_override is not None:
            stop_reason = stop_override
            break
        support.extend(chosen)
        support_mask[np.asarray(chosen, dtype=int)] = True

        with PhaseTimer(phase_timings, "solve"):
            coef, solver_name = solve_least_squares(Phi[:, support], y)
        if solver_name != "lstsq":
            fallback_reason = solver_name
            solver_fallback_count += 1

        with PhaseTimer(phase_timings, "residual_update"):
            x_hat[:] = 0.0
            x_hat[np.asarray(support, dtype=int)] = coef
            residual = y - Phi @ x_hat
            residual_norm = float(np.linalg.norm(residual))
        residual_history.append(residual_norm)
        support_history.append(sorted(support.copy()))
        support_condition_history.append(estimate_condition_number(Phi[:, support]))

        if k is not None and len(support) >= k:
            stop_reason = "target_sparsity_reached"
            break
        if residual_norm <= tol:
            stop_reason = "residual_tol"
            break

    info = _build_info(
        group_size=group_size,
        support_history=support_history,
        residual_history=residual_history,
        support_size=len(support),
        iteration_count=len(residual_history) - 1,
        support_condition_history=support_condition_history,
        stop_reason=stop_reason,
        fallback_reason=fallback_reason,
        solver_fallback_count=solver_fallback_count,
        duplicate_candidate_hits=duplicate_candidate_hits,
        runtime_sec=time.perf_counter() - t0,
        implementation="baseline",
        used_incremental_solver=False,
        profile_level=profile_level,
        phase_timings=phase_timings,
        memory_breakdown=build_memory_breakdown(
            residual=residual,
            x_hat=x_hat,
            support_mask=support_mask,
            support_history=support_history,
            residual_history=residual_history,
            support_condition_history=support_condition_history,
        ),
    )
    return x_hat, np.asarray(sorted(support), dtype=int), info


def _gomp_optimized(
    Phi: np.ndarray,
    y: np.ndarray,
    group_size: int,
    k: int | None,
    tol: float,
    max_iter: int,
    profile_level: str,
) -> tuple[np.ndarray, np.ndarray, dict]:
    _, n = Phi.shape
    support: list[int] = []
    support_mask = np.zeros(n, dtype=bool)
    residual = y.copy()
    residual_history = [float(np.linalg.norm(residual))]
    support_history: list[list[int]] = []
    stop_reason = "max_iter"
    fallback_reason = ""
    solver_fallback_count = 0
    duplicate_candidate_hits = 0
    support_condition_history: list[float] = []
    phase_timings = init_phase_timing()
    t0 = time.perf_counter()
    light_profile = profile_level == "light"
    final_coef = np.zeros(0, dtype=float)
    for _ in range(max_iter):
        with PhaseTimer(phase_timings, "correlation"):
            corr = np.abs(Phi.T @ residual)
            corr[support_mask] = -np.inf
        with PhaseTimer(phase_timings, "selection"):
            chosen, stop_override, duplicate_hits = _select_group(corr, support_mask, group_size, k, len(support))
        duplicate_candidate_hits += duplicate_hits
        if stop_override is not None:
            stop_reason = stop_override
            break
        support.extend(chosen)
        support_mask[np.asarray(chosen, dtype=int)] = True

        with PhaseTimer(phase_timings, "solve"):
            Phi_support = Phi[:, support]
            coef, solver_name = stable_solve_gram(Phi_support.T @ Phi_support, Phi_support.T @ y)
        if solver_name != "gram_solve":
            fallback_reason = solver_name
            solver_fallback_count += 1
        final_coef = coef

        with PhaseTimer(phase_timings, "residual_update"):
            projection = Phi[:, support] @ coef
            residual = y - projection
            residual_norm = float(np.linalg.norm(residual))
        residual_history.append(residual_norm)
        if not light_profile:
            support_history.append(sorted(support.copy()))

        if k is not None and len(support) >= k:
            stop_reason = "target_sparsity_reached"
            break
        if residual_norm <= tol:
            stop_reason = "residual_tol"
            break

    if light_profile and support:
        support_history.append(sorted(support.copy()))
    if support:
        support_condition_history = [estimate_condition_number(Phi[:, support])]

    x_hat = np.zeros(n, dtype=float)
    if support:
        x_hat[np.asarray(support, dtype=int)] = final_coef

    info = _build_info(
        group_size=group_size,
        support_history=support_history,
        residual_history=residual_history,
        support_size=len(support),
        iteration_count=len(residual_history) - 1,
        support_condition_history=support_condition_history,
        stop_reason=stop_reason,
        fallback_reason=fallback_reason,
        solver_fallback_count=solver_fallback_count,
        duplicate_candidate_hits=duplicate_candidate_hits,
        runtime_sec=time.perf_counter() - t0,
        implementation="optimized",
        used_incremental_solver=True,
        profile_level=profile_level,
        phase_timings=phase_timings,
        memory_breakdown=build_memory_breakdown(
            residual=residual,
            x_hat=None,
            support_mask=support_mask,
            support_history=support_history,
            residual_history=residual_history,
            support_condition_history=support_condition_history,
        ),
    )
    return x_hat, np.asarray(sorted(support), dtype=int), info


def gomp(
    Phi: np.ndarray,
    y: np.ndarray,
    group_size: int = 2,
    k: int | None = None,
    tol: float | None = None,
    max_iter: int | None = None,
    implementation: str = "optimized",
    profile_level: str = "full",
    return_info: bool = True,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    Generalized OMP with explicit baseline and optimized paths.
    """
    m, _ = Phi.shape
    if group_size <= 0:
        raise ValueError("group_size must be positive")
    max_iter = max_iter or min(m, max(1, (k or m) // max(group_size, 1) + 1))
    tol = float(tol) if tol is not None else 1e-8

    if implementation == "baseline":
        x_hat, support_hat, info = _gomp_baseline(
            Phi=Phi, y=y, group_size=group_size, k=k, tol=tol, max_iter=max_iter, profile_level=profile_level
        )
    elif implementation == "optimized":
        x_hat, support_hat, info = _gomp_optimized(
            Phi=Phi, y=y, group_size=group_size, k=k, tol=tol, max_iter=max_iter, profile_level=profile_level
        )
    else:
        raise ValueError("implementation must be 'baseline' or 'optimized'")
    return x_hat, support_hat, info if return_info else {}
