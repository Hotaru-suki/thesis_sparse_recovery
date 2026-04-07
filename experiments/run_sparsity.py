from __future__ import annotations

from experiments.cli import load_cli_config
from experiments.common import make_standard_plots, run_sweep


def main() -> None:
    config = load_cli_config("sparsity", "Run sparsity sweep experiment")

    _, summary_df, paths = run_sweep(
        experiment_name="sparsity",
        config=config,
        sweep_name="k",
        sweep_values=config["k_list"],
        k_selector=lambda value, _: int(value),
        matrix_selector=lambda _, cfg: cfg["matrix_kind"],
        snr_selector=lambda _, cfg: cfg.get("snr_db"),
    )
    make_standard_plots(
        summary_df,
        x_col="k",
        figure_specs=[
            ("sparsity_exact_support.png", "exact_support_recovery", "Exact support recovery"),
            ("sparsity_nmse.png", "nmse", "NMSE"),
            ("sparsity_runtime.png", "runtime_sec", "Runtime (sec)"),
        ],
        figure_dir=paths["figures"],
    )


if __name__ == "__main__":
    main()
