from __future__ import annotations

from experiments.cli import load_cli_config
from experiments.common import make_standard_plots, run_sweep


def main() -> None:
    config = load_cli_config("runtime", "Run runtime sweep experiment")

    _, summary_df, paths = run_sweep(
        experiment_name="runtime",
        config=config,
        sweep_name="n",
        sweep_values=config["n_list"],
        k_selector=lambda value, cfg: min(int(cfg["k"]), max(1, int(value) // 8)),
        matrix_selector=lambda _, cfg: cfg["matrix_kind"],
        snr_selector=lambda _, cfg: cfg.get("snr_db"),
    )
    make_standard_plots(
        summary_df,
        x_col="n",
        figure_specs=[("runtime_compare.png", "runtime_sec", "Runtime (sec)")],
        figure_dir=paths["figures"],
    )


if __name__ == "__main__":
    main()
