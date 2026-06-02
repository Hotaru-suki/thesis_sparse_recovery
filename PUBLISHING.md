# Publishing Guide

## Recommended Public Artifact Set

For a clean public repository, keep:

- source code under `algorithms/`, `utils/`, `experiments/`, and `tests/`
- experiment presets under `configs/`
- documentation under `docs/`
- entrypoints and repository metadata such as `README.md`, `requirements.txt`, `LICENSE`, `CONTRIBUTING.md`, and `REPRODUCIBILITY.md`
- reproducible result artifacts under `results/raw/`, `results/aggregated/`, and `figures/`

## Usually Excluded

- local virtual environments
- IDE metadata
- transient cache files
- timestamped run logs under `results/logs/`
- local scratch files
- temporary comparison directories such as `tmp_*`
- local thesis-generation scratch scripts unless they are intentionally documented

## Suggested Output Policy

If you want the repository to stay compact while still being reproducible:

- keep all files in `results/aggregated/`
- keep the matching `figures/` set
- keep `results/raw/` only if trial-level reproducibility is important to the public release

If you prefer a lighter release, a reasonable minimum is:

- `results/aggregated/*.csv`
- `figures/*.png`

## Pre-Publish Review

- check that `README.md` matches the current repository positioning
- check that `docs/` uses public-facing wording rather than internal project framing
- check that tracked results correspond to the latest run you want to present
- check that no private machine paths or local scratch files remain
- check that `git status` does not include accidental environment or cache files
- run `python -m pytest`
