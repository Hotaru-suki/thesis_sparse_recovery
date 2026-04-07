from __future__ import annotations

import numpy as np

try:
    from scipy.fft import dct
except Exception:  # pragma: no cover
    dct = None


def normalize_columns(Phi: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(Phi, axis=0, keepdims=True)
    norms = np.where(norms < 1e-12, 1.0, norms)
    return Phi / norms


def generate_sparse_signal(
    n: int,
    k: int,
    coeff_mode: str = "gaussian",
    normalized: bool = False,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    if not 0 < k <= n:
        raise ValueError(f"k must satisfy 0 < k <= n, got k={k}, n={n}")
    rng = rng or np.random.default_rng()
    x = np.zeros(n, dtype=float)
    support = np.sort(rng.choice(n, size=k, replace=False))
    if coeff_mode == "gaussian":
        x[support] = rng.standard_normal(k)
    elif coeff_mode == "rademacher":
        x[support] = rng.choice([-1.0, 1.0], size=k)
    elif coeff_mode == "uniform":
        x[support] = rng.uniform(-1.0, 1.0, size=k)
    else:
        raise ValueError(f"Unsupported coeff_mode={coeff_mode}")
    if normalized:
        norm = float(np.linalg.norm(x))
        if norm > 1e-12:
            x /= norm
    return x, support


def _partial_dct_matrix(m: int, n: int, rng: np.random.Generator) -> np.ndarray:
    if dct is None:
        raise RuntimeError("scipy is required for partial_dct matrix generation")
    basis = dct(np.eye(n), axis=0, norm="ortho")
    rows = np.sort(rng.choice(n, size=m, replace=False))
    return basis[rows, :]


def generate_measurement_matrix(
    m: int,
    n: int,
    kind: str = "gaussian",
    normalize_columns_flag: bool = True,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    if not 0 < m <= n:
        raise ValueError(f"m must satisfy 0 < m <= n, got m={m}, n={n}")
    rng = rng or np.random.default_rng()
    if kind == "gaussian":
        Phi = rng.standard_normal((m, n)) / np.sqrt(m)
    elif kind == "bernoulli":
        Phi = rng.choice([-1.0, 1.0], size=(m, n)) / np.sqrt(m)
    elif kind == "partial_dct":
        Phi = _partial_dct_matrix(m, n, rng)
    elif kind == "correlated_gaussian":
        base = rng.standard_normal((m, n))
        shared = rng.standard_normal((m, 1))
        Phi = (0.75 * base + 0.25 * shared) / np.sqrt(m)
    else:
        raise ValueError(f"Unsupported matrix kind={kind}")
    return normalize_columns(Phi) if normalize_columns_flag else Phi


def add_noise(
    y_clean: np.ndarray,
    snr_db: float | None = None,
    sigma: float | None = None,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, float]:
    rng = rng or np.random.default_rng()
    if sigma is not None and sigma < 0:
        raise ValueError("sigma must be non-negative")
    if sigma is None and snr_db is None:
        return y_clean.copy(), 0.0
    if sigma is None:
        signal_power = max(float(np.mean(y_clean**2)), 1e-12)
        noise_power = signal_power / (10 ** (float(snr_db) / 10.0))
        sigma = float(np.sqrt(noise_power))
    noise = rng.standard_normal(y_clean.shape) * float(sigma)
    return y_clean + noise, float(sigma)


def sample_problem(
    m: int,
    n: int,
    k: int,
    rng: np.random.Generator,
    matrix_kind: str = "gaussian",
    coeff_mode: str = "gaussian",
    snr_db: float | None = None,
    sigma: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    Phi = generate_measurement_matrix(m=m, n=n, kind=matrix_kind, rng=rng)
    x_true, support = generate_sparse_signal(n=n, k=k, coeff_mode=coeff_mode, rng=rng)
    y_clean = Phi @ x_true
    y, noise_sigma = add_noise(y_clean, snr_db=snr_db, sigma=sigma, rng=rng)
    return Phi, x_true, support, y, noise_sigma
