from __future__ import annotations

from experiments.cli import load_cli_config
from experiments.common import _run_gomp, _run_improved, make_standard_plots, run_sweep


def main() -> None:
    config = load_cli_config("ablation", "Run ablation experiment")

    algorithm_specs = {
        "gOMP": (_run_gomp, config),
        "gOMP+AdaptiveScreen": (_run_improved, {**config, "use_incremental_solver": False, "use_noise_aware_stop": False}),
        "gOMP+IncrementalSolver": (_run_improved, {**config, "screening_ratio": 1.0, "use_noise_aware_stop": False}),
        "gOMP+NoiseAwareStop": (_run_improved, {**config, "screening_ratio": 1.0, "use_incremental_solver": False, "use_noise_aware_stop": True}),
        "gOMP+Adaptive+Incremental": (_run_improved, {**config, "use_noise_aware_stop": False}),
        "gOMP+Adaptive+NoiseAware": (_run_improved, {**config, "use_incremental_solver": False, "use_noise_aware_stop": True}),
        "gOMP+Incremental+NoiseAware": (_run_improved, {**config, "screening_ratio": 1.0, "use_noise_aware_stop": True}),
        "Improved-gOMP": (_run_improved, config),
    }

    _, summary_df, paths = run_sweep(
        experiment_name="ablation",
        config=config,
        sweep_name="ablation_variant",
        sweep_values=["full_suite"],
        k_selector=lambda _, cfg: int(cfg["k"]),
        matrix_selector=lambda _, cfg: cfg["matrix_kind"],
        snr_selector=lambda _, cfg: cfg.get("snr_db"),
        algorithm_specs=algorithm_specs,
    )
    make_standard_plots(
        summary_df,
        x_col="algorithm",
        figure_specs=[
            ("ablation_runtime.png", "runtime_sec", "Runtime (sec)"),
            ("ablation_nmse.png", "nmse", "NMSE"),
            ("ablation_exact_support.png", "exact_support_recovery", "Exact support recovery"),
        ],
        figure_dir=paths["figures"],
    )


if __name__ == "__main__":
    main()
