from __future__ import annotations

import time

import numpy as np

from utils.linalg import (
    IncrementalGramSolver,
    PhaseTimer,
    estimate_condition_number,
    init_phase_timing,
    solve_least_squares,
)
from utils.memory import build_memory_breakdown


def _build_info(
    *,
    support_history: list[list[int]],
    residual_history: list[float],
    support_size: int,
    iteration_count: int,
    support_condition_history: list[float],
    rescale_history: list[float],
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
        "screening_pool_size_avg": 1.0 if support_history else 0.0,
        "rescale_history": rescale_history,
        "avg_rescale_alpha": float(np.mean(rescale_history)) if rescale_history else 0.0,
        "support_condition_history": support_condition_history,
        "max_support_condition": float(max(support_condition_history)) if support_condition_history else 0.0,
        "implementation": implementation,
        "timing_breakdown_sec": dict(phase_timings),
        "memory_breakdown_bytes": dict(memory_breakdown),
        "peak_working_set_bytes": int(memory_breakdown.get("peak_working_set_bytes", 0)),
    }


def _rescale_update(
    *,
    Phi: np.ndarray,
    y: np.ndarray,
    support: list[int],
    coef: np.ndarray,
    x_hat: np.ndarray,
    rescale_factor: float,
    rescale_mode: str = "fixed",
) -> tuple[np.ndarray, np.ndarray, float, str]:
    projection = Phi[:, support] @ coef
    fallback_reason = ""
    if rescale_mode == "fixed":
        alpha = float(rescale_factor)
    else:
        denom = float(projection @ projection)
        if denom > 1e-12:
            alpha = float((projection @ y) / denom)
        else:
            alpha = float(rescale_factor)
            fallback_reason = "degenerate_rescale_direction"
    alpha = max(alpha, 0.0)
    x_hat[:] = 0.0
    x_hat[np.asarray(support, dtype=int)] = alpha * coef
    residual = y - Phi @ x_hat
    return residual, projection, alpha, fallback_reason


def _rmp_baseline(
    Phi: np.ndarray,
    y: np.ndarray,
    k: int | None,
    tol: float,
    max_iter: int,
    rescale_factor: float,
    profile_level: str,
    rescale_mode: str = "fixed",
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
    solver_time_history: list[float] = []
    rescale_history: list[float] = []
    duplicate_candidate_hits = 0
    support_condition_history: list[float] = []
    solver_fallback_count = 0
    phase_timings = init_phase_timing()
    t0 = time.perf_counter()

    for _ in range(max_iter):
        with PhaseTimer(phase_timings, "correlation"):
            corr = Phi.T @ residual
            corr[support_mask] = 0.0
        with PhaseTimer(phase_timings, "selection"):
            new_idx = int(np.argmax(np.abs(corr)))
        if support_mask[new_idx]:
            duplicate_candidate_hits += 1
            stop_reason = "empty_candidate_set"
            break
        support.append(new_idx)
        support_mask[new_idx] = True

        solve_t0 = time.perf_counter()
        with PhaseTimer(phase_timings, "solve"):
            coef, solver_name = solve_least_squares(Phi[:, support], y)
        solver_time_history.append(time.perf_counter() - solve_t0)
        if solver_name != "lstsq":
            fallback_reason = solver_name
            solver_fallback_count += 1

        support_condition_history.append(estimate_condition_number(Phi[:, support]))
        with PhaseTimer(phase_timings, "residual_update"):
            residual, _, alpha, rescale_fallback = _rescale_update(
                Phi=Phi,
                y=y,
                support=support,
                coef=coef,
                x_hat=x_hat,
                rescale_factor=rescale_factor,
                rescale_mode=rescale_mode,
            )
            residual_norm = float(np.linalg.norm(residual))
        if rescale_fallback:
            fallback_reason = fallback_reason or rescale_fallback
        rescale_history.append(alpha)
        residual_history.append(residual_norm)
        support_history.append(sorted(support.copy()))

        if residual_norm <= tol:
            stop_reason = "residual_tol"
            break
        if k is not None and len(support) >= k:
            stop_reason = "target_sparsity_reached"
            break

    if support:
        support_condition_history = [estimate_condition_number(Phi[:, support])]

    info = _build_info(
        support_history=support_history,
        residual_history=residual_history,
        support_size=len(support),
        iteration_count=len(residual_history) - 1,
        support_condition_history=support_condition_history,
        rescale_history=rescale_history,
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
    info["solver_time_history"] = solver_time_history
    return x_hat, np.asarray(sorted(support), dtype=int), info


def _rmp_optimized(
    Phi: np.ndarray,
    y: np.ndarray,
    k: int | None,
    tol: float,
    max_iter: int,
    rescale_factor: float,
    profile_level: str,
    rescale_mode: str = "fixed",
) -> tuple[np.ndarray, np.ndarray, dict]:
    _, n = Phi.shape
    residual = y.copy()
    support: list[int] = []
    support_mask = np.zeros(n, dtype=bool)
    residual_history = [float(np.linalg.norm(residual))]
    support_history: list[list[int]] = []
    stop_reason = "max_iter"
    fallback_reason = ""
    solver_fallback_count = 0
    duplicate_candidate_hits = 0
    support_condition_history: list[float] = []
    rescale_history: list[float] = []
    phase_timings = init_phase_timing()
    t0 = time.perf_counter()
    solver = IncrementalGramSolver(Phi=Phi, y=y)
    light_profile = profile_level == "light"
    final_coef = np.zeros(0, dtype=float)
    final_alpha = 0.0

    for _ in range(max_iter):
        with PhaseTimer(phase_timings, "correlation"):
            corr = Phi.T @ residual
            corr[support_mask] = 0.0
        with PhaseTimer(phase_timings, "selection"):
            new_idx = int(np.argmax(np.abs(corr)))
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
        if solver_name != "gram_solve":
            fallback_reason = solver_name
            solver_fallback_count += 1
        final_coef = coef
        working_x = np.zeros(n, dtype=float)
        with PhaseTimer(phase_timings, "residual_update"):
            residual, _, alpha, rescale_fallback = _rescale_update(
                Phi=Phi,
                y=y,
                support=support,
                coef=coef,
                x_hat=working_x,
                rescale_factor=rescale_factor,
                rescale_mode=rescale_mode,
            )
            residual_norm = float(np.linalg.norm(residual))
        if rescale_fallback:
            fallback_reason = fallback_reason or rescale_fallback
        rescale_history.append(alpha)
        final_alpha = alpha
        residual_history.append(residual_norm)
        if not light_profile:
            support_history.append(sorted(support.copy()))

        if residual_norm <= tol:
            stop_reason = "residual_tol"
            break
        if k is not None and len(support) >= k:
            stop_reason = "target_sparsity_reached"
            break

    if light_profile and support:
        support_history.append(sorted(support.copy()))
    if support:
        support_condition_history = [estimate_condition_number(Phi[:, support])]
    x_hat = np.zeros(n, dtype=float)
    if support:
        x_hat[np.asarray(support, dtype=int)] = final_alpha * final_coef

    info = _build_info(
        support_history=support_history,
        residual_history=residual_history,
        support_size=len(support),
        iteration_count=len(residual_history) - 1,
        support_condition_history=support_condition_history,
        rescale_history=rescale_history,
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


def rmp(
    Phi: np.ndarray,
    y: np.ndarray,
    k: int | None = None,
    tol: float | None = None,
    max_iter: int | None = None,
    rescale_factor: float = 0.5,
    rescale_mode: str = "fixed",
    implementation: str = "optimized",
    profile_level: str = "full",
    return_info: bool = True,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    Experimental rescaled matching pursuit with explicit baseline and optimized paths.
    """
    m, n = Phi.shape
    max_iter = max_iter or (k if k is not None else min(m, n))
    tol = float(tol) if tol is not None else 1e-8

    if implementation == "baseline":
        x_hat, support_hat, info = _rmp_baseline(
            Phi=Phi,
            y=y,
            k=k,
            tol=tol,
            max_iter=max_iter,
            rescale_factor=rescale_factor,
            profile_level=profile_level,
            rescale_mode=rescale_mode,
        )
    elif implementation == "optimized":
        x_hat, support_hat, info = _rmp_optimized(
            Phi=Phi,
            y=y,
            k=k,
            tol=tol,
            max_iter=max_iter,
            rescale_factor=rescale_factor,
            profile_level=profile_level,
            rescale_mode=rescale_mode,
        )
    else:
        raise ValueError("implementation must be 'baseline' or 'optimized'")
    return x_hat, support_hat, info if return_info else {}
