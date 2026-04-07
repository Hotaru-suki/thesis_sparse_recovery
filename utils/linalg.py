from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def solve_least_squares(Phi_s: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, str]:
    """Solve a least-squares problem with a stable fallback."""
    if Phi_s.size == 0:
        return np.zeros(0, dtype=float), "empty_support"
    try:
        coef, *_ = np.linalg.lstsq(Phi_s, y, rcond=None)
        return coef, "lstsq"
    except np.linalg.LinAlgError:
        coef = np.linalg.pinv(Phi_s) @ y
        return coef, "pinv_fallback"


def stable_solve_gram(gram: np.ndarray, rhs: np.ndarray, ridge: float = 1e-10) -> tuple[np.ndarray, str]:
    if gram.size == 0:
        return np.zeros(0, dtype=float), "empty_support"
    system = gram.copy()
    system.flat[:: system.shape[0] + 1] += ridge
    try:
        return np.linalg.solve(system, rhs), "gram_solve"
    except np.linalg.LinAlgError:
        coef, *_ = np.linalg.lstsq(system, rhs, rcond=None)
        return coef, "gram_lstsq_fallback"


def estimate_condition_number(matrix: np.ndarray) -> float:
    if matrix.size == 0:
        return 0.0
    try:
        return float(np.linalg.cond(matrix))
    except np.linalg.LinAlgError:
        return float("inf")


@dataclass
class IncrementalGramSolver:
    """Maintain Gram-system caches for support growth."""

    Phi: np.ndarray
    y: np.ndarray
    ridge: float = 1e-10

    def __post_init__(self) -> None:
        self.support: list[int] = []
        self.gram = np.zeros((0, 0), dtype=float)
        self.rhs = np.zeros(0, dtype=float)

    def extend(self, new_indices: list[int]) -> None:
        for idx in new_indices:
            idx = int(idx)
            if idx in self.support:
                continue
            col = self.Phi[:, idx]
            if not self.support:
                self.gram = np.array([[float(col @ col)]], dtype=float)
                self.rhs = np.array([float(col @ self.y)], dtype=float)
            else:
                cross = self.Phi[:, self.support].T @ col
                gram_new = np.zeros((len(self.support) + 1, len(self.support) + 1), dtype=float)
                gram_new[:-1, :-1] = self.gram
                gram_new[:-1, -1] = cross
                gram_new[-1, :-1] = cross
                gram_new[-1, -1] = float(col @ col)
                self.gram = gram_new
                self.rhs = np.concatenate([self.rhs, [float(col @ self.y)]])
            self.support.append(idx)

    def solve(self) -> tuple[np.ndarray, str]:
        return stable_solve_gram(self.gram, self.rhs, ridge=self.ridge)


def topk_indices(values: np.ndarray, k: int) -> np.ndarray:
    if k <= 0:
        return np.array([], dtype=int)
    k = min(k, values.size)
    idx = np.argpartition(-values, kth=k - 1)[:k]
    return idx[np.argsort(-values[idx])]
