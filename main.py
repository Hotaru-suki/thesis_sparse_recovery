from __future__ import annotations

import argparse
import subprocess
import sys


EXPERIMENT_MODULES = {
    "sparsity": "experiments.run_sparsity",
    "snr": "experiments.run_snr",
    "runtime": "experiments.run_runtime",
    "compression": "experiments.run_compression",
    "matrix_type": "experiments.run_matrix_type",
    "coeff_mode": "experiments.run_coeff_mode",
    "ablation": "experiments.run_ablation",
    "param_sensitivity": "experiments.run_param_sensitivity",
}


def run_module(module_name: str, seed: int | None, trials: int | None, outdir: str | None) -> None:
    cmd = [sys.executable, "-m", module_name]
    if seed is not None:
        cmd.extend(["--seed", str(seed)])
    if trials is not None:
        cmd.extend(["--trials", str(trials)])
    if outdir is not None:
        cmd.extend(["--outdir", outdir])
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sparse recovery thesis experiment runner")
    parser.add_argument("--all", action="store_true", help="run all configured experiments")
    parser.add_argument("--exp", choices=sorted(EXPERIMENT_MODULES.keys()))
    parser.add_argument("--seed", type=int)
    parser.add_argument("--trials", type=int)
    parser.add_argument("--outdir", type=str, default=".")
    args = parser.parse_args()

    if args.all:
        for module_name in EXPERIMENT_MODULES.values():
            run_module(module_name, args.seed, args.trials, args.outdir)
        return
    if args.exp:
        run_module(EXPERIMENT_MODULES[args.exp], args.seed, args.trials, args.outdir)
        return
    parser.error("Use --all or --exp {sparsity,snr,runtime,compression,matrix_type,coeff_mode,ablation,param_sensitivity}.")


if __name__ == "__main__":
    main()
