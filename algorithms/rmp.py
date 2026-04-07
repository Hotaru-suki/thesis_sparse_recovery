from __future__ import annotations

import time

import numpy as np

from utils.linalg import estimate_condition_number, solve_least_squares


def rmp(
    Phi: np.ndarray,
    y: np.ndarray,
    k: int | None = None,
    tol: float | None = None,
    max_iter: int | None = None,
    rescale_factor: float = 0.5,
    return_info: bool = True,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    Experimental rescaled matching pursuit style comparator.

    This is a bounded engineering approximation for [14]. The rescaling step is
    chosen by minimizing the current residual norm along the least-squares
    update direction, which is more stable than a fixed blend factor while
    still staying within the project's controlled-comparator boundary.
    """
    m, n = Phi.shape
    max_iter = max_iter or (k if k is not None else min(m, n))
    tol = float(tol) if tol is not None else 1e-8
    residual = y.copy()
    x_hat = np.zeros(n, dtype=float)
    support: list[int] = []
    residual_history = [float(np.linalg.norm(residual))]
    support_history: list[list[int]] = []
    stop_reason = "max_iter"
    fallback_reason = ""
    solver_time_history: list[float] = []
    rescale_history: list[float] = []
    duplicate_candidate_hits = 0
    support_condition_history: list[float] = []
    solver_fallback_count = 0
    t0 = time.perf_counter()

    for _ in range(max_iter):
        corr = Phi.T @ residual
        if support:
            corr[np.asarray(support, dtype=int)] = 0.0
        new_idx = int(np.argmax(np.abs(corr)))
        if new_idx in support:
            duplicate_candidate_hits += 1
            stop_reason = "empty_candidate_set"
            break
        support.append(new_idx)

        solve_t0 = time.perf_counter()
        coef, solver_name = solve_least_squares(Phi[:, support], y)
        solver_time_history.append(time.perf_counter() - solve_t0)
        if solver_name != "lstsq":
            fallback_reason = solver_name
            solver_fallback_count += 1

        proposal = np.zeros(n, dtype=float)
        proposal[np.asarray(support, dtype=int)] = coef
        support_condition_history.append(estimate_condition_number(Phi[:, support]))
        projected = Phi @ proposal
        denom = float(projected @ projected)
        if denom > 1e-12:
            alpha = float((projected @ y) / denom)
        else:
            alpha = float(rescale_factor)
            fallback_reason = fallback_reason or "degenerate_rescale_direction"
        alpha = max(alpha, 0.0)
        rescale_history.append(alpha)

        x_hat[:] = alpha * proposal
        residual = y - Phi @ x_hat
        residual_norm = float(np.linalg.norm(residual))
        residual_history.append(residual_norm)
        support_history.append(sorted(support.copy()))

        if residual_norm <= tol:
            stop_reason = "residual_tol"
            break
        if k is not None and len(support) >= k:
            stop_reason = "target_sparsity_reached"
            break

    info = {
        "iterations": len(support_history),
        "runtime_sec": time.perf_counter() - t0,
        "residual_history": residual_history,
        "support_history": support_history,
        "support_size_history": [len(s) for s in support_history],
        "stop_reason": stop_reason,
        "fallback_reason": fallback_reason,
        "solver_fallback_count": solver_fallback_count,
        "duplicate_candidate_hits": duplicate_candidate_hits,
        "solver_time_history": solver_time_history,
        "used_incremental_solver": False,
        "screening_pool_size_avg": 1.0 if support_history else 0.0,
        "rescale_history": rescale_history,
        "avg_rescale_alpha": float(np.mean(rescale_history)) if rescale_history else 0.0,
        "support_condition_history": support_condition_history,
        "max_support_condition": float(max(support_condition_history)) if support_condition_history else 0.0,
    }
    return x_hat, np.asarray(sorted(support), dtype=int), info if return_info else {}
