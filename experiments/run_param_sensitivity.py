from __future__ import annotations

import pandas as pd

from experiments.cli import load_cli_config
from experiments.common import _run_improved, run_trials, summarize
from utils.io_utils import ensure_output_dirs, save_results, save_run_metadata
from utils.plotting import plot_metric


def _sensitivity_params(config: dict, **overrides: object) -> dict:
    params = {**config, **overrides}
    # Parameter-sensitivity runs need diagnostic histories such as
    # candidate_size_history; optimized sweeps default to light profiling.
    params["optimized_profile_level"] = "full"
    return params


def main() -> None:
    config = load_cli_config("param_sensitivity", "Run parameter sensitivity experiment")

    paths = ensure_output_dirs(config["outdir"])
    raw_parts = []
    for screening_ratio in config["screening_ratio_list"]:
        raw_parts.append(
            run_trials(
                m=config["m"],
                n=config["n"],
                k=config["k"],
                variable_name="screening_ratio",
                variable_value=screening_ratio,
                trials=config["trials"],
                seed=config["seed"] + int(screening_ratio * 10),
                matrix_kind=config["matrix_kind"],
                coeff_mode=config.get("coeff_mode", "gaussian"),
                snr_db=config.get("snr_db"),
                sigma=config.get("sigma"),
                algorithm_specs=[
                    {
                        "algorithm": "Improved-gOMP",
                        "implementation": "optimized",
                        "algorithm_fn": _run_improved,
                        "params": _sensitivity_params(
                            config,
                            screening_ratio=screening_ratio,
                            improved_screening_ratio=screening_ratio,
                            optimized_screening_ratio=screening_ratio,
                        ),
                    }
                ],
            )
        )
    for group_size in config["group_size_list"]:
        raw_parts.append(
            run_trials(
                m=config["m"],
                n=config["n"],
                k=config["k"],
                variable_name="group_size",
                variable_value=group_size,
                trials=config["trials"],
                seed=config["seed"] + int(group_size * 100),
                matrix_kind=config["matrix_kind"],
                coeff_mode=config.get("coeff_mode", "gaussian"),
                snr_db=config.get("snr_db"),
                sigma=config.get("sigma"),
                algorithm_specs=[
                    {
                        "algorithm": "Improved-gOMP",
                        "implementation": "optimized",
                        "algorithm_fn": _run_improved,
                        "params": _sensitivity_params(
                            config,
                            group_size=group_size,
                            improved_group_size=group_size,
                        ),
                    }
                ],
            )
        )

    raw_df = pd.concat(raw_parts, ignore_index=True)
    screening_summary = summarize(raw_df[raw_df["screening_ratio"].notna()], "screening_ratio") if "screening_ratio" in raw_df.columns else pd.DataFrame()
    group_summary = summarize(raw_df[raw_df["group_size"].notna()], "group_size") if "group_size" in raw_df.columns else pd.DataFrame()
    summary_df = pd.concat([screening_summary, group_summary], ignore_index=True, sort=False)

    save_results(raw_df, summary_df, paths["raw"] / "param_sensitivity.csv", paths["aggregated"] / "summary_param_sensitivity.csv")
    save_run_metadata(paths["logs"], experiment_name="param_sensitivity", config=config)
    if not screening_summary.empty:
        plot_metric(screening_summary, "screening_ratio", "nmse", paths["figures"] / "param_screening_ratio.png", "screening ratio", "screening_ratio", "NMSE")
    if not group_summary.empty:
        plot_metric(group_summary, "group_size", "nmse", paths["figures"] / "param_group_size.png", "group size", "group_size", "NMSE")


if __name__ == "__main__":
    main()
