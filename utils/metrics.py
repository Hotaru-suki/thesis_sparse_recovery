from __future__ import annotations

import numpy as np


def nmse(x_true: np.ndarray, x_hat: np.ndarray) -> float:
    denom = max(float(np.linalg.norm(x_true) ** 2), 1e-12)
    return float(np.linalg.norm(x_true - x_hat) ** 2 / denom)


def relative_l2_error(x_true: np.ndarray, x_hat: np.ndarray) -> float:
    denom = max(float(np.linalg.norm(x_true)), 1e-12)
    return float(np.linalg.norm(x_true - x_hat) / denom)


def support_recall(s_true: np.ndarray, s_hat: np.ndarray) -> float:
    if len(s_true) == 0:
        return 1.0
    inter = len(set(map(int, s_true)).intersection(set(map(int, s_hat))))
    return float(inter / len(s_true))


def support_precision(s_true: np.ndarray, s_hat: np.ndarray) -> float:
    if len(s_hat) == 0:
        return 0.0
    inter = len(set(map(int, s_true)).intersection(set(map(int, s_hat))))
    return float(inter / len(s_hat))


def exact_support_recovery(s_true: np.ndarray, s_hat: np.ndarray) -> int:
    return int(set(map(int, s_true)) == set(map(int, s_hat)))


def final_residual_norm(Phi: np.ndarray, x_hat: np.ndarray, y: np.ndarray) -> float:
    return float(np.linalg.norm(y - Phi @ x_hat))


def false_positive_count(s_true: np.ndarray, s_hat: np.ndarray) -> int:
    return len(set(map(int, s_hat)).difference(set(map(int, s_true))))


def false_negative_count(s_true: np.ndarray, s_hat: np.ndarray) -> int:
    return len(set(map(int, s_true)).difference(set(map(int, s_hat))))
