from __future__ import annotations

from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from tqdm import tqdm

from algorithms import gomp, improved_gomp, omp, rmp
from utils.data_gen import sample_problem
from utils.io_utils import ensure_output_dirs, save_results, save_run_metadata
from utils.metrics import (
    exact_support_recovery,
    false_negative_count,
    false_positive_count,
    final_residual_norm,
    nmse,
    relative_l2_error,
    support_precision,
    support_recall,
)
from utils.plotting import plot_metric


AlgorithmFn = Callable[[np.ndarray, np.ndarray, int, float | None, dict], tuple[np.ndarray, np.ndarray, dict]]


def _run_omp(Phi: np.ndarray, y: np.ndarray, k: int, noise_sigma: float | None, params: dict) -> tuple[np.ndarray, np.ndarray, dict]:
    return omp(Phi=Phi, y=y, k=k, tol=params.get("tol"), max_iter=params.get("max_iter"))


def _run_gomp(Phi: np.ndarray, y: np.ndarray, k: int,

              noise_sigma: float | None, params: dict) -> tuple[np.ndarray, np.ndarray, dict]:
    return gomp(
        Phi=Phi,
        y=y,
        k=k,
        group_size=params.get("group_size", 2),
        tol=params.get("tol"),
        max_iter=params.get("max_iter"),
    )


def _run_improved(Phi: np.ndarray, y: np.ndarray, k: int, noise_sigma: float | None, params: dict) -> tuple[np.ndarray, np.ndarray, dict]:
    return improved_gomp(
        Phi=Phi,
        y=y,
        k=k,
        group_size=params.get("group_size", 2),
        tol=params.get("tol"),
        max_iter=params.get("max_iter"),
        screening_ratio=params.get("screening_ratio", 3.0),
        min_group_size=params.get("min_group_size", 1),
        use_noise_aware_stop=params.get("use_noise_aware_stop", True),
        use_incremental_solver=params.get("use_incremental_solver", True),
        noise_sigma=noise_sigma,
        min_residual_drop=params.get("min_residual_drop", 1e-4),
    )


def _run_rmp(Phi: np.ndarray, y: np.ndarray, k: int, noise_sigma: float | None, params: dict) -> tuple[np.ndarray, np.ndarray, dict]:
    return rmp(
        Phi=Phi,
        y=y,
        k=k,
        tol=params.get("tol"),
        max_iter=params.get("max_iter"),
        rescale_factor=params.get("rescale_factor", 0.5),
    )


BASELINE_ALGORITHMS: dict[str, AlgorithmFn] = {
    "OMP": _run_omp,
    "gOMP": _run_gomp,
    "Improved-gOMP": _run_improved,
}


def build_default_algorithm_specs(config: dict) -> dict[str, tuple[AlgorithmFn, dict]]:
    algorithm_specs = {name: (fn, config) for name, fn in BASELINE_ALGORITHMS.items()}
    if config.get("include_rmp", False):
        algorithm_specs["RMP"] = (_run_rmp, config)
    return algorithm_specs


def run_trials(
    *,
    m: int,
    n: int,
    k: int,
    variable_name: str,
    variable_value: object,
    trials: int,
    seed: int,
    matrix_kind: str,
    coeff_mode: str,
    snr_db: float | None,
    sigma: float | None,
    algorithm_specs: dict[str, tuple[AlgorithmFn, dict]],
) -> pd.DataFrame:
    rows = []
    base_rng = np.random.default_rng(seed)
    trial_seeds = base_rng.integers(0, 2**31 - 1, size=trials)

    for trial_idx, trial_seed in enumerate(tqdm(trial_seeds, leave=False, desc=f"{variable_name}={variable_value}")):
        rng = np.random.default_rng(int(trial_seed))
        Phi, x_true, support_true, y, noise_sigma = sample_problem(
            m=m,
            n=n,
            k=k,
            rng=rng,
            matrix_kind=matrix_kind,
            coeff_mode=coeff_mode,
            snr_db=snr_db,
            sigma=sigma,
        )

        for algorithm_name, (algorithm_fn, params) in algorithm_specs.items():
            x_hat, support_hat, info = algorithm_fn(Phi, y, k, noise_sigma, params)
            rows.append(
                {
                    "trial": trial_idx,
                    variable_name: variable_value,
                    "algorithm": algorithm_name,
                    "m": m,
                    "n": n,
                    "measurement_ratio": float(m / max(n, 1)),
                    "matrix_kind": matrix_kind,
                    "coeff_mode": coeff_mode,
                    "snr_db": snr_db if snr_db is not None else "clean",
                    "noise_sigma": noise_sigma,
                    "nmse": nmse(x_true, x_hat),
                    "relative_l2_error": relative_l2_error(x_true, x_hat),
                    "support_recall": support_recall(support_true, support_hat),
                    "support_precision": support_precision(support_true, support_hat),
                    "exact_support_recovery": exact_support_recovery(support_true, support_hat),
                    "runtime_sec": info["runtime_sec"],
                    "iterations": info["iterations"],
                    "final_residual_norm": final_residual_norm(Phi, x_hat, y),
                    "stop_reason": info["stop_reason"],
                    "false_positive_count": false_positive_count(support_true, support_hat),
                    "false_negative_count": false_negative_count(support_true, support_hat),
                    "solver_time_sec": float(sum(info.get("solver_time_history", []))),
                    "screening_pool_size_avg": info.get("screening_pool_size_avg", 0.0),
                    "used_incremental_solver": info.get("used_incremental_solver", False),
                    "fallback_reason": info.get("fallback_reason", ""),
                    "solver_fallback_count": info.get("solver_fallback_count", 0),
                    "duplicate_candidate_hits": info.get("duplicate_candidate_hits", 0),
                    "max_support_condition": info.get("max_support_condition", 0.0),
                }
            )
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame, variable_name: str) -> pd.DataFrame:
    metric_cols = [
        "nmse",
        "relative_l2_error",
        "support_recall",
        "support_precision",
        "exact_support_recovery",
        "runtime_sec",
        "iterations",
        "final_residual_norm",
        "false_positive_count",
        "false_negative_count",
        "solver_time_sec",
        "screening_pool_size_avg",
        "solver_fallback_count",
        "duplicate_candidate_hits",
        "max_support_condition",
    ]
    return df.groupby([variable_name, "algorithm"], as_index=False)[metric_cols].mean(numeric_only=True)


def run_sweep(
    *,
    experiment_name: str,
    config: dict,
    sweep_name: str,
    sweep_values: list,
    m_selector: Callable[[object, dict], int] | None = None,
    k_selector: Callable[[object, dict], int],
    matrix_selector: Callable[[object, dict], str],
    coeff_selector: Callable[[object, dict], str] | None = None,
    snr_selector: Callable[[object, dict], float | None],
    algorithm_specs: dict[str, tuple[AlgorithmFn, dict]] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Path]]:
    paths = ensure_output_dirs(config["outdir"])
    algorithm_specs = algorithm_specs or build_default_algorithm_specs(config)

    all_raw = []
    for value in sweep_values:
        current_m = int(m_selector(value, config)) if m_selector is not None else int(config["m"])
        raw_df = run_trials(
            m=current_m,
            n=config["n"],
            k=k_selector(value, config),
            variable_name=sweep_name,
            variable_value=value,
            trials=config["trials"],
            seed=config["seed"] + int(abs(hash(str(value))) % 10000),
            matrix_kind=matrix_selector(value, config),
            coeff_mode=coeff_selector(value, config) if coeff_selector is not None else config.get("coeff_mode", "gaussian"),
            snr_db=snr_selector(value, config),
            sigma=config.get("sigma"),
            algorithm_specs=algorithm_specs,
        )
        all_raw.append(raw_df)

    raw_df = pd.concat(all_raw, ignore_index=True)
    summary_df = summarize(raw_df, variable_name=sweep_name)
    save_results(
        raw_df,
        summary_df,
        paths["raw"] / f"{experiment_name}.csv",
        paths["aggregated"] / f"summary_{experiment_name}.csv",
    )
    save_run_metadata(paths["logs"], experiment_name=experiment_name, config=config)
    return raw_df, summary_df, paths


def make_standard_plots(summary_df: pd.DataFrame, x_col: str, figure_specs: list[tuple[str, str, str]], figure_dir: Path) -> None:
    for filename, metric, ylabel in figure_specs:
        plot_metric(
            summary_df,
            x_col=x_col,
            y_col=metric,
            out_path=figure_dir / filename,
            title=filename.replace(".png", "").replace("_", " "),
            xlabel=x_col,
            ylabel=ylabel,
        )
