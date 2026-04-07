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


AlgorithmFn = Callable[[np.ndarray, np.ndarray, int, float | None, dict, str], tuple[np.ndarray, np.ndarray, dict]]

PHASE_COLUMNS = [
    "correlation_time_sec",
    "selection_time_sec",
    "solve_time_sec",
    "residual_update_time_sec",
    "support_refinement_time_sec",
]

MEMORY_COLUMNS = [
    "peak_working_set_bytes",
    "residual_bytes",
    "x_hat_bytes",
    "support_mask_bytes",
    "solver_gram_bytes",
    "solver_rhs_bytes",
    "support_history_bytes",
    "residual_history_bytes",
    "support_size_history_bytes",
    "candidate_size_history_bytes",
    "group_size_history_bytes",
    "support_condition_history_bytes",
    "extra_array_bytes",
]


def _slugify_algorithm(name: str) -> str:
    return name.lower().replace("-", "_")


def _profile_level_for(params: dict, implementation: str) -> str:
    default_level = "light" if implementation == "optimized" else "full"
    return str(params.get(f"{implementation}_profile_level", params.get("profile_level", default_level)))


def build_improved_gomp_kwargs(params: dict, noise_sigma: float | None, implementation: str) -> dict:
    optimized_profile_level = _profile_level_for(params, "optimized")
    baseline_profile_level = _profile_level_for(params, "baseline")
    if implementation == "baseline":
        return {
            "implementation": implementation,
            "profile_level": baseline_profile_level,
            "group_size": params.get("improved_group_size", params.get("group_size", 2)),
            "tol": params.get("tol"),
            "max_iter": params.get("max_iter"),
            "screening_ratio": params.get("baseline_screening_ratio", max(params.get("improved_screening_ratio", params.get("screening_ratio", 3.0)), 3.0)),
            "min_group_size": params.get("improved_min_group_size", params.get("min_group_size", 1)),
            "use_noise_aware_stop": params.get("use_noise_aware_stop", True),
            "use_incremental_solver": params.get("baseline_use_incremental_solver", False),
            "noise_sigma": noise_sigma,
            "min_residual_drop": params.get("baseline_min_residual_drop", min(params.get("improved_min_residual_drop", params.get("min_residual_drop", 1e-4)), 5e-5)),
            "use_tail_refinement": params.get("baseline_use_tail_refinement", True),
            "use_gain_reranking": params.get("baseline_use_gain_reranking", True),
            "use_forward_backward": params.get("baseline_use_forward_backward", True),
            "use_two_phase_tail": params.get("baseline_use_two_phase_tail", True),
            "use_cholesky_solver": params.get("baseline_use_cholesky_solver", False),
        }
    return {
        "implementation": implementation,
        "profile_level": optimized_profile_level,
        "group_size": params.get("improved_group_size", params.get("group_size", 2)),
        "tol": params.get("tol"),
        "max_iter": params.get("max_iter"),
        "screening_ratio": params.get("optimized_screening_ratio", min(params.get("improved_screening_ratio", params.get("screening_ratio", 3.0)), 2.0)),
        "min_group_size": params.get("improved_min_group_size", params.get("min_group_size", 1)),
        "use_noise_aware_stop": params.get("use_noise_aware_stop", True),
        "use_incremental_solver": params.get("optimized_use_incremental_solver", params.get("use_incremental_solver", True)),
        "noise_sigma": noise_sigma,
        "min_residual_drop": params.get("optimized_min_residual_drop", params.get("improved_min_residual_drop", params.get("min_residual_drop", 1e-4))),
        "use_tail_refinement": params.get("optimized_use_tail_refinement", False),
        "use_gain_reranking": params.get("optimized_use_gain_reranking", False),
        "use_forward_backward": params.get("optimized_use_forward_backward", False),
        "use_two_phase_tail": params.get("optimized_use_two_phase_tail", False),
        "use_cholesky_solver": params.get("optimized_use_cholesky_solver", params.get("use_cholesky_solver", True)),
    }


def _run_omp(
    Phi: np.ndarray, y: np.ndarray, k: int, noise_sigma: float | None, params: dict, implementation: str
) -> tuple[np.ndarray, np.ndarray, dict]:
    del noise_sigma
    return omp(
        Phi=Phi,
        y=y,
        k=k,
        tol=params.get("tol"),
        max_iter=params.get("max_iter"),
        implementation=implementation,
        profile_level=_profile_level_for(params, implementation),
    )


def _run_gomp(
    Phi: np.ndarray, y: np.ndarray, k: int, noise_sigma: float | None, params: dict, implementation: str
) -> tuple[np.ndarray, np.ndarray, dict]:
    del noise_sigma
    return gomp(
        Phi=Phi,
        y=y,
        k=k,
        group_size=params.get("group_size", 2),
        tol=params.get("tol"),
        max_iter=params.get("max_iter"),
        implementation=implementation,
        profile_level=_profile_level_for(params, implementation),
    )


def _run_improved(
    Phi: np.ndarray, y: np.ndarray, k: int, noise_sigma: float | None, params: dict, implementation: str
) -> tuple[np.ndarray, np.ndarray, dict]:
    return improved_gomp(Phi=Phi, y=y, k=k, **build_improved_gomp_kwargs(params, noise_sigma, implementation))


def _run_rmp(
    Phi: np.ndarray, y: np.ndarray, k: int, noise_sigma: float | None, params: dict, implementation: str
) -> tuple[np.ndarray, np.ndarray, dict]:
    del noise_sigma
    return rmp(
        Phi=Phi,
        y=y,
        k=k,
        tol=params.get("tol"),
        max_iter=params.get("max_iter"),
        rescale_factor=params.get("rescale_factor", 0.5),
        implementation=implementation,
        profile_level=_profile_level_for(params, implementation),
    )


BASELINE_ALGORITHMS: dict[str, AlgorithmFn] = {
    "OMP": _run_omp,
    "gOMP": _run_gomp,
    "Improved-gOMP": _run_improved,
}


def build_default_algorithm_specs(config: dict) -> list[dict[str, object]]:
    specs: list[dict[str, object]] = []
    algorithm_map = dict(BASELINE_ALGORITHMS)
    if config.get("include_rmp", False):
        algorithm_map["RMP"] = _run_rmp
    for algorithm_name, algorithm_fn in algorithm_map.items():
        for implementation in ("baseline", "optimized"):
            specs.append(
                {
                    "algorithm": algorithm_name,
                    "implementation": implementation,
                    "algorithm_fn": algorithm_fn,
                    "params": config,
                }
            )
    return specs


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
    algorithm_specs: list[dict[str, object]],
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

        for spec in algorithm_specs:
            algorithm_name = str(spec["algorithm"])
            implementation = str(spec["implementation"])
            algorithm_fn = spec["algorithm_fn"]
            params = dict(spec["params"])
            x_hat, support_hat, info = algorithm_fn(Phi, y, k, noise_sigma, params, implementation)
            timing_breakdown = info.get("timing_breakdown_sec", {})
            memory_breakdown = info.get("memory_breakdown_bytes", {})
            rows.append(
                {
                    "trial": trial_idx,
                    variable_name: variable_value,
                    "algorithm": algorithm_name,
                    "implementation": implementation,
                    "label": f"{algorithm_name} ({implementation})",
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
                    "support_size": float(len(support_hat)),
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
                    "rescue_attempted": float(bool(info.get("rescue_attempted", False))),
                    "rescue_accepted": float(bool(info.get("rescue_accepted", False))),
                    "used_tail_refinement": float(bool(info.get("used_tail_refinement", False))),
                    "used_gain_reranking": float(bool(info.get("used_gain_reranking", False))),
                    "used_forward_backward": float(bool(info.get("used_forward_backward", False))),
                    "used_two_phase_tail": float(bool(info.get("used_two_phase_tail", False))),
                    "used_cholesky_solver": float(bool(info.get("used_cholesky_solver", False))),
                    "peak_working_set_bytes": float(info.get("peak_working_set_bytes", 0.0)),
                    "residual_bytes": float(memory_breakdown.get("residual_bytes", 0.0)),
                    "x_hat_bytes": float(memory_breakdown.get("x_hat_bytes", 0.0)),
                    "support_mask_bytes": float(memory_breakdown.get("support_mask_bytes", 0.0)),
                    "solver_gram_bytes": float(memory_breakdown.get("solver_gram_bytes", 0.0)),
                    "solver_rhs_bytes": float(memory_breakdown.get("solver_rhs_bytes", 0.0)),
                    "support_history_bytes": float(memory_breakdown.get("support_history_bytes", 0.0)),
                    "residual_history_bytes": float(memory_breakdown.get("residual_history_bytes", 0.0)),
                    "support_size_history_bytes": float(memory_breakdown.get("support_size_history_bytes", 0.0)),
                    "candidate_size_history_bytes": float(memory_breakdown.get("candidate_size_history_bytes", 0.0)),
                    "group_size_history_bytes": float(memory_breakdown.get("group_size_history_bytes", 0.0)),
                    "support_condition_history_bytes": float(memory_breakdown.get("support_condition_history_bytes", 0.0)),
                    "extra_array_bytes": float(memory_breakdown.get("extra_array_bytes", 0.0)),
                    "correlation_time_sec": float(timing_breakdown.get("correlation", 0.0)),
                    "selection_time_sec": float(timing_breakdown.get("selection", 0.0)),
                    "solve_time_sec": float(timing_breakdown.get("solve", 0.0)),
                    "residual_update_time_sec": float(timing_breakdown.get("residual_update", 0.0)),
                    "support_refinement_time_sec": float(timing_breakdown.get("support_refinement", 0.0)),
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
        "support_size",
        "final_residual_norm",
        "false_positive_count",
        "false_negative_count",
        "solver_time_sec",
        "screening_pool_size_avg",
        "solver_fallback_count",
        "duplicate_candidate_hits",
        "max_support_condition",
        "rescue_attempted",
        "rescue_accepted",
        "used_tail_refinement",
        "used_gain_reranking",
        "used_forward_backward",
        "used_two_phase_tail",
        "used_cholesky_solver",
        *PHASE_COLUMNS,
        *MEMORY_COLUMNS,
    ]
    return df.groupby([variable_name, "algorithm", "implementation"], as_index=False)[metric_cols].mean(numeric_only=True)


def build_speedup_summary(df: pd.DataFrame, variable_name: str) -> dict[str, pd.DataFrame]:
    outputs: dict[str, pd.DataFrame] = {}
    merge_keys = [variable_name, "algorithm"]
    metric_cols = ["runtime_sec", "nmse", "support_recall", "support_precision", "exact_support_recovery"]
    baseline = df[df["implementation"] == "baseline"][merge_keys + metric_cols].rename(
        columns={col: f"baseline_{col}" for col in metric_cols}
    )
    optimized = df[df["implementation"] == "optimized"][merge_keys + metric_cols].rename(
        columns={col: f"optimized_{col}" for col in metric_cols}
    )
    merged = baseline.merge(optimized, on=merge_keys, how="inner")
    if merged.empty:
        return outputs
    merged["speedup_ratio"] = merged["baseline_runtime_sec"] / merged["optimized_runtime_sec"].clip(lower=1e-12)
    merged["nmse_delta"] = merged["optimized_nmse"] - merged["baseline_nmse"]
    merged["support_recall_delta"] = merged["optimized_support_recall"] - merged["baseline_support_recall"]
    merged["support_precision_delta"] = merged["optimized_support_precision"] - merged["baseline_support_precision"]
    merged["exact_support_recovery_delta"] = (
        merged["optimized_exact_support_recovery"] - merged["baseline_exact_support_recovery"]
    )
    for algorithm_name, group in merged.groupby("algorithm"):
        outputs[algorithm_name] = group.drop(columns="algorithm").reset_index(drop=True)
    return outputs


def build_memory_speedup_summary(df: pd.DataFrame, variable_name: str) -> dict[str, pd.DataFrame]:
    outputs: dict[str, pd.DataFrame] = {}
    merge_keys = [variable_name, "algorithm"]
    metric_cols = ["peak_working_set_bytes", "solver_gram_bytes", "support_history_bytes"]
    baseline = df[df["implementation"] == "baseline"][merge_keys + metric_cols].rename(
        columns={col: f"baseline_{col}" for col in metric_cols}
    )
    optimized = df[df["implementation"] == "optimized"][merge_keys + metric_cols].rename(
        columns={col: f"optimized_{col}" for col in metric_cols}
    )
    merged = baseline.merge(optimized, on=merge_keys, how="inner")
    if merged.empty:
        return outputs
    merged["memory_saving_ratio"] = merged["baseline_peak_working_set_bytes"] / merged["optimized_peak_working_set_bytes"].clip(lower=1e-12)
    merged["peak_working_set_delta_bytes"] = merged["optimized_peak_working_set_bytes"] - merged["baseline_peak_working_set_bytes"]
    merged["solver_gram_delta_bytes"] = merged["optimized_solver_gram_bytes"] - merged["baseline_solver_gram_bytes"]
    merged["support_history_delta_bytes"] = merged["optimized_support_history_bytes"] - merged["baseline_support_history_bytes"]
    for algorithm_name, group in merged.groupby("algorithm"):
        outputs[algorithm_name] = group.drop(columns="algorithm").reset_index(drop=True)
    return outputs


def save_runtime_breakdowns(
    raw_df: pd.DataFrame, summary_df: pd.DataFrame, variable_name: str, experiment_name: str, paths: dict[str, Path]
) -> None:
    for algorithm_name, group in raw_df.groupby("algorithm"):
        slug = _slugify_algorithm(algorithm_name)
        suffix = "" if experiment_name == "runtime" else f"_{experiment_name}"
        breakdown_cols = [variable_name, "trial", "algorithm", "implementation", "runtime_sec", *PHASE_COLUMNS]
        group[breakdown_cols].to_csv(paths["raw"] / f"runtime_breakdown_{slug}{suffix}.csv", index=False)
        summary_group = summary_df[summary_df["algorithm"] == algorithm_name][
            [variable_name, "algorithm", "implementation", "runtime_sec", *PHASE_COLUMNS]
        ]
        summary_group.to_csv(paths["aggregated"] / f"summary_runtime_breakdown_{slug}{suffix}.csv", index=False)


def save_memory_breakdowns(
    raw_df: pd.DataFrame, summary_df: pd.DataFrame, variable_name: str, experiment_name: str, paths: dict[str, Path]
) -> None:
    for algorithm_name, group in raw_df.groupby("algorithm"):
        slug = _slugify_algorithm(algorithm_name)
        suffix = "" if experiment_name == "runtime" else f"_{experiment_name}"
        breakdown_cols = [variable_name, "trial", "algorithm", "implementation", *MEMORY_COLUMNS]
        group[breakdown_cols].to_csv(paths["raw"] / f"memory_breakdown_{slug}{suffix}.csv", index=False)
        summary_group = summary_df[summary_df["algorithm"] == algorithm_name][
            [variable_name, "algorithm", "implementation", *MEMORY_COLUMNS]
        ]
        summary_group.to_csv(paths["aggregated"] / f"summary_memory_breakdown_{slug}{suffix}.csv", index=False)


def save_speedup_summaries(summary_df: pd.DataFrame, variable_name: str, experiment_name: str, paths: dict[str, Path]) -> None:
    speedup_tables = build_speedup_summary(summary_df, variable_name)
    for algorithm_name, table in speedup_tables.items():
        suffix = "" if experiment_name == "runtime" else f"_{experiment_name}"
        table.to_csv(paths["aggregated"] / f"summary_speedup_{_slugify_algorithm(algorithm_name)}{suffix}.csv", index=False)


def save_memory_speedup_summaries(summary_df: pd.DataFrame, variable_name: str, experiment_name: str, paths: dict[str, Path]) -> None:
    memory_tables = build_memory_speedup_summary(summary_df, variable_name)
    for algorithm_name, table in memory_tables.items():
        suffix = "" if experiment_name == "runtime" else f"_{experiment_name}"
        table.to_csv(paths["aggregated"] / f"summary_memory_speedup_{_slugify_algorithm(algorithm_name)}{suffix}.csv", index=False)


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
    algorithm_specs: list[dict[str, object]] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Path]]:
    paths = ensure_output_dirs(config["outdir"])
    algorithm_specs = algorithm_specs or build_default_algorithm_specs(config)

    all_raw = []
    for value in sweep_values:
        current_m = int(m_selector(value, config)) if m_selector is not None else int(config["m"])
        current_n = int(value) if sweep_name == "n" else int(config["n"])
        raw_df = run_trials(
            m=current_m,
            n=current_n,
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
    save_runtime_breakdowns(raw_df, summary_df, sweep_name, experiment_name, paths)
    save_memory_breakdowns(raw_df, summary_df, sweep_name, experiment_name, paths)
    save_speedup_summaries(summary_df, sweep_name, experiment_name, paths)
    save_memory_speedup_summaries(summary_df, sweep_name, experiment_name, paths)
    save_run_metadata(paths["logs"], experiment_name=experiment_name, config=config)
    return raw_df, summary_df, paths


def make_standard_plots(summary_df: pd.DataFrame, x_col: str, figure_specs: list[tuple[str, str, str]], figure_dir: Path) -> None:
    plot_df = summary_df[summary_df["implementation"] == "optimized"].copy()
    for filename, metric, ylabel in figure_specs:
        plot_metric(
            plot_df,
            x_col=x_col,
            y_col=metric,
            out_path=figure_dir / filename,
            title=filename.replace(".png", "").replace("_", " "),
            xlabel=x_col,
            ylabel=ylabel,
        )
