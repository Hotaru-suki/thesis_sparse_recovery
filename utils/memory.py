from __future__ import annotations

from typing import Any

import numpy as np


def array_nbytes(array: np.ndarray | None) -> int:
    return 0 if array is None else int(array.nbytes)


def list_capacity_bytes(values: list[Any], item_bytes: int = 8) -> int:
    return int(len(values) * item_bytes)


def nested_int_lists_bytes(values: list[list[int]], item_bytes: int = 8) -> int:
    return int(sum(len(inner) for inner in values) * item_bytes)


def build_memory_breakdown(
    *,
    residual: np.ndarray | None = None,
    x_hat: np.ndarray | None = None,
    support_mask: np.ndarray | None = None,
    solver_gram: np.ndarray | None = None,
    solver_rhs: np.ndarray | None = None,
    support_history: list[list[int]] | None = None,
    residual_history: list[float] | None = None,
    support_size_history: list[int] | None = None,
    candidate_size_history: list[int] | None = None,
    group_size_history: list[int] | None = None,
    support_condition_history: list[float] | None = None,
    extra_arrays: list[np.ndarray] | None = None,
) -> dict[str, int]:
    breakdown = {
        "residual_bytes": array_nbytes(residual),
        "x_hat_bytes": array_nbytes(x_hat),
        "support_mask_bytes": array_nbytes(support_mask),
        "solver_gram_bytes": array_nbytes(solver_gram),
        "solver_rhs_bytes": array_nbytes(solver_rhs),
        "support_history_bytes": nested_int_lists_bytes(support_history or []),
        "residual_history_bytes": list_capacity_bytes(residual_history or []),
        "support_size_history_bytes": list_capacity_bytes(support_size_history or []),
        "candidate_size_history_bytes": list_capacity_bytes(candidate_size_history or []),
        "group_size_history_bytes": list_capacity_bytes(group_size_history or []),
        "support_condition_history_bytes": list_capacity_bytes(support_condition_history or []),
        "extra_array_bytes": int(sum(array_nbytes(array) for array in (extra_arrays or []))),
    }
    breakdown["peak_working_set_bytes"] = int(sum(breakdown.values()))
    return breakdown
