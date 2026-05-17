from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

import numpy as np


PHASE_NAMES = (
    "correlation",
    "selection",
    "solve",
    "residual_update",
    "support_refinement",
)


def init_phase_timing() -> dict[str, float]:
    return {phase: 0.0 for phase in PHASE_NAMES}


@dataclass
class PhaseTimer:
    timings: dict[str, float]
    phase: str

    def __enter__(self) -> "PhaseTimer":
        self._t0 = perf_counter()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.timings[self.phase] = self.timings.get(self.phase, 0.0) + (perf_counter() - self._t0)


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

    def snapshot(self) -> tuple[list[int], np.ndarray, np.ndarray]:
        return self.support.copy(), self.gram.copy(), self.rhs.copy()

    def restore(self, state: tuple[list[int], np.ndarray, np.ndarray]) -> None:
        support, gram, rhs = state
        self.support = support.copy()
        self.gram = gram.copy()
        self.rhs = rhs.copy()

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
        if self.gram.size == 0:
            return np.zeros(0, dtype=float), "empty_support"
        for multiplier in [1.0, 100.0, 10000.0]:
            ridge = max(self.ridge * multiplier, self.ridge)
            coef, solver_name = stable_solve_gram(self.gram, self.rhs, ridge=ridge)
            if solver_name == "gram_solve":
                return coef, solver_name
        return stable_solve_gram(self.gram, self.rhs, ridge=1e-2)


@dataclass
class IncrementalCholeskySolver:
    """Maintain Gram-system caches with a Cholesky-first solve path."""

    Phi: np.ndarray
    y: np.ndarray
    ridge: float = 1e-10

    def __post_init__(self) -> None:
        self.support: list[int] = []
        self.gram = np.zeros((0, 0), dtype=float)
        self.rhs = np.zeros(0, dtype=float)

    def snapshot(self) -> tuple[list[int], np.ndarray, np.ndarray]:
        return self.support.copy(), self.gram.copy(), self.rhs.copy()

    def restore(self, state: tuple[list[int], np.ndarray, np.ndarray]) -> None:
        support, gram, rhs = state
        self.support = support.copy()
        self.gram = gram.copy()
        self.rhs = rhs.copy()

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
        if self.gram.size == 0:
            return np.zeros(0, dtype=float), "empty_support"
        for attempt, multiplier in enumerate([1.0, 100.0, 10000.0]):
            ridge = max(self.ridge * multiplier, self.ridge)
            try:
                system = self.gram.copy()
                system.flat[:: system.shape[0] + 1] += ridge
                chol = np.linalg.cholesky(system)
                z = np.linalg.solve(chol, self.rhs)
                coef = np.linalg.solve(chol.T, z)
                return coef, "cholesky_solve"
            except np.linalg.LinAlgError:
                if attempt == 2:
                    return stable_solve_gram(self.gram, self.rhs, ridge=max(ridge, 1e-2))
        return stable_solve_gram(self.gram, self.rhs, ridge=1e-2)


def topk_indices(values: np.ndarray, k: int) -> np.ndarray:
    if k <= 0:
        return np.array([], dtype=int)
    k = min(k, values.size)
    idx = np.argpartition(-values, kth=k - 1)[:k]
    return idx[np.argsort(-values[idx])]


def compute_gram_and_rhs(Phi: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return Phi.T @ Phi, Phi.T @ y


def solve_from_cached_gram(
    gram: np.ndarray,
    phi_ty: np.ndarray,
    support: list[int],
    ridge: float = 1e-10,
) -> tuple[np.ndarray, str]:
    if not support:
        return np.zeros(0, dtype=float), "empty_support"
    support_idx = np.asarray(support, dtype=int)
    return stable_solve_gram(gram[np.ix_(support_idx, support_idx)], phi_ty[support_idx], ridge=ridge)
