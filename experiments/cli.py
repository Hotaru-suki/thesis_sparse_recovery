from __future__ import annotations

import argparse

from experiments.config import get_config_path
from utils.io_utils import load_config


def load_cli_config(config_name: str, description: str) -> dict:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--config", type=str, default=str(get_config_path(config_name)))
    parser.add_argument("--seed", type=int)
    parser.add_argument("--trials", type=int)
    parser.add_argument("--outdir", type=str)
    args = parser.parse_args()

    config = load_config(args.config)
    if args.seed is not None:
        config["seed"] = args.seed
    if args.trials is not None:
        config["trials"] = args.trials
    if args.outdir is not None:
        config["outdir"] = args.outdir
    return config
