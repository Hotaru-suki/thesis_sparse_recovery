from __future__ import annotations

import time

import numpy as np

from utils.linalg import (
    IncrementalCholeskySolver,
    PhaseTimer,
    estimate_condition_number,
    init_phase_timing,
    solve_least_squares,
    topk_indices,
)
from utils.memory import build_memory_breakdown


def _build_info(
    *,
    support: list[int],
    support_history: list[list[int]],
    residual_history: list[float],
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
        "support_size_history": [len(s) for s in support_history] if support_history else ([len(support)] if support else []),
        "stop_reason": stop_reason,
        "fallback_reason": fallback_reason,
        "solver_fallback_count": solver_fallback_count,
        "duplicate_candidate_hits": duplicate_candidate_hits,
        "solver_time_history": [phase_timings.get("solve", 0.0)],
        "used_incremental_solver": used_incremental_solver,
        "profile_level": profile_level,
        "screening_pool_size_avg": 1.0 if support_history else 0.0,
        "support_condition_history": support_condition_history,
        "max_support_condition": float(max(support_condition_history)) if support_condition_history else 0.0,
        "implementation": implementation,
        "timing_breakdown_sec": dict(phase_timings),
        "memory_breakdown_bytes": dict(memory_breakdown),
        "peak_working_set_bytes": int(memory_breakdown.get("peak_working_set_bytes", 0)),
    }


def _omp_baseline(
    Phi: np.ndarray,
    y: np.ndarray,
    k: int | None,
    tol: float,
    max_iter: int,
    profile_level: str,
) -> tuple[np.ndarray, np.ndarray, dict]:
    _, n = Phi.shape
    residual = y.copy()
    x_hat = np.zeros(n, dtype=float)
    support: list[int] = []
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
            if support:
                corr[np.asarray(support, dtype=int)] = -np.inf
        with PhaseTimer(phase_timings, "selection"):
            new_idx = int(topk_indices(corr, 1)[0])
        if new_idx in support:
            duplicate_candidate_hits += 1
            stop_reason = "empty_candidate_set"
            break
        support.append(new_idx)
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
        support=support,
        support_history=support_history,
        residual_history=residual_history,
        iteration_count=len(support),
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
            support_history=support_history,
            residual_history=residual_history,
            support_condition_history=support_condition_history,
        ),
    )
    return x_hat, np.asarray(sorted(support), dtype=int), info


def _omp_optimized(
    Phi: np.ndarray,
    y: np.ndarray,
    k: int | None,
    tol: float,
    max_iter: int,
    profile_level: str,
) -> tuple[np.ndarray, np.ndarray, dict]:
    _, n = Phi.shape
    support: list[int] = []
    support_mask = np.zeros(n, dtype=bool)
    support_history: list[list[int]] = []
    support_condition_history: list[float] = []
    residual = y.copy()
    residual_history = [float(np.linalg.norm(residual))]
    stop_reason = "max_iter"
    fallback_reason = ""
    solver_fallback_count = 0
    duplicate_candidate_hits = 0
    phase_timings = init_phase_timing()
    t0 = time.perf_counter()
    solver = IncrementalCholeskySolver(Phi=Phi, y=y)
    final_coef = np.zeros(0, dtype=float)

    light_profile = profile_level == "light"
    for _ in range(max_iter):
        with PhaseTimer(phase_timings, "correlation"):
            corr = np.abs(Phi.T @ residual)
            corr[support_mask] = -np.inf
        with PhaseTimer(phase_timings, "selection"):
            new_idx = int(np.argmax(corr))
        if support_mask[new_idx]:
            duplicate_candidate_hits += 1
            stop_reason = "empty_candidate_set"
            break
        support.append(new_idx)
        support_mask[new_idx] = True

        with PhaseTimer(phase_timings, "support_refinement"):
            solver.extend([new_idx])
        with PhaseTimer(phase_timings, "solve"):
            coef, solver_name = solver.solve()
        if solver_name not in {"cholesky_solve", "gram_solve"}:
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
        support=support,
        support_history=support_history,
        residual_history=residual_history,
        iteration_count=len(support),
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
            solver_gram=solver.gram,
            solver_rhs=solver.rhs,
            support_history=support_history,
            residual_history=residual_history,
            support_condition_history=support_condition_history,
        ),
    )
    return x_hat, np.asarray(sorted(support), dtype=int), info


def omp(
    Phi: np.ndarray,
    y: np.ndarray,
    k: int | None = None,
    tol: float | None = None,
    max_iter: int | None = None,
    implementation: str = "optimized",
    profile_level: str = "full",
    return_info: bool = True,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Orthogonal Matching Pursuit with explicit baseline and optimized paths."""
    m, n = Phi.shape
    max_iter = max_iter or (k if k is not None else min(m, n))
    tol = float(tol) if tol is not None else 1e-8

    if implementation == "baseline":
        x_hat, support_hat, info = _omp_baseline(Phi=Phi, y=y, k=k, tol=tol, max_iter=max_iter, profile_level=profile_level)
    elif implementation == "optimized":
        x_hat, support_hat, info = _omp_optimized(Phi=Phi, y=y, k=k, tol=tol, max_iter=max_iter, profile_level=profile_level)
    else:
        raise ValueError("implementation must be 'baseline' or 'optimized'")
    return x_hat, support_hat, info if return_info else {}
