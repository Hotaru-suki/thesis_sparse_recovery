from __future__ import annotations

from experiments.cli import load_cli_config
from experiments.common import make_standard_plots, run_sweep


def main() -> None:
    config = load_cli_config("compression", "Run measurement-ratio sweep experiment")

    _, summary_df, paths = run_sweep(
        experiment_name="compression",
        config=config,
        sweep_name="measurement_ratio",
        sweep_values=config["measurement_ratio_list"],
        m_selector=lambda value, cfg: max(int(round(float(value) * int(cfg["n"]))), int(cfg["min_m"])),
        k_selector=lambda _, cfg: int(cfg["k"]),
        matrix_selector=lambda _, cfg: cfg["matrix_kind"],
        coeff_selector=lambda _, cfg: cfg.get("coeff_mode", "gaussian"),
        snr_selector=lambda _, cfg: cfg.get("snr_db"),
    )
    make_standard_plots(
        summary_df,
        x_col="measurement_ratio",
        figure_specs=[
            ("compression_exact_support.png", "exact_support_recovery", "Exact support recovery"),
            ("compression_nmse.png", "nmse", "NMSE"),
            ("compression_runtime.png", "runtime_sec", "Runtime (sec)"),
        ],
        figure_dir=paths["figures"],
    )


if __name__ == "__main__":
    main()
