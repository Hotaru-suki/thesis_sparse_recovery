from __future__ import annotations

from experiments.cli import load_cli_config
from experiments.common import make_standard_plots, run_sweep


def main() -> None:
    config = load_cli_config("coeff_mode", "Run coefficient-mode sweep experiment")

    _, summary_df, paths = run_sweep(
        experiment_name="coeff_mode",
        config=config,
        sweep_name="coeff_mode",
        sweep_values=config["coeff_mode_list"],
        k_selector=lambda _, cfg: int(cfg["k"]),
        matrix_selector=lambda _, cfg: cfg["matrix_kind"],
        coeff_selector=lambda value, _: str(value),
        snr_selector=lambda _, cfg: cfg.get("snr_db"),
    )
    make_standard_plots(
        summary_df,
        x_col="coeff_mode",
        figure_specs=[
            ("coeff_mode_exact_support.png", "exact_support_recovery", "Exact support recovery"),
            ("coeff_mode_nmse.png", "nmse", "NMSE"),
            ("coeff_mode_runtime.png", "runtime_sec", "Runtime (sec)"),
        ],
        figure_dir=paths["figures"],
    )


if __name__ == "__main__":
    main()
