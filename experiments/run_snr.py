from __future__ import annotations

from experiments.cli import load_cli_config
from experiments.common import make_standard_plots, run_sweep


def main() -> None:
    config = load_cli_config("snr", "Run SNR sweep experiment")

    _, summary_df, paths = run_sweep(
        experiment_name="snr",
        config=config,
        sweep_name="snr_db",
        sweep_values=config["snr_list"],
        k_selector=lambda _, cfg: int(cfg["k"]),
        matrix_selector=lambda _, cfg: cfg["matrix_kind"],
        snr_selector=lambda value, _: None if value == "clean" else float(value),
    )
    make_standard_plots(
        summary_df,
        x_col="snr_db",
        figure_specs=[
            ("snr_nmse.png", "nmse", "NMSE"),
            ("snr_support_recall.png", "support_recall", "Support recall"),
            ("snr_runtime.png", "runtime_sec", "Runtime (sec)"),
        ],
        figure_dir=paths["figures"],
    )


if __name__ == "__main__":
    main()
