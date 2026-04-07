# GitHub Submission Notes

This repository is already organized in a form suitable for public version control hosting.

## Recommended Contents

- source code: `algorithms/`, `utils/`, `experiments/`, `tests/`
- configuration: `configs/`
- documentation: `docs/`
- entrypoints and dependencies: `main.py`, `requirements.txt`, `README.md`
- reproducible outputs you want to publish:
  - `results/raw/`
  - `results/aggregated/`
  - `figures/`

## Usually Excluded

- `.venv/`
- `__pycache__/`
- `.idea/`
- timestamped run logs under `results/logs/`

These exclusions are already reflected in [`.gitignore`](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/.gitignore).

## Recommended Repository Description

When publishing the repository, the homepage description should make these points clear:

- this is a sparse-recovery experiment repository, not a general-purpose library
- the main comparison path is `OMP`, `gOMP`, and `Improved-gOMP`
- `RMP` is included as an exploratory implementation
- `results/` and `figures/` contain reproducible benchmark artifacts

See also [PUBLISHING.md](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/PUBLISHING.md) for a compact public-artifact policy.

## Suggested Submission Flow

```bash
git init
git add .
git status
git commit -m "Initial sparse recovery experiment repository"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

## Pre-Publish Checks

- `README.md` matches the current project entrypoints
- `configs/` all load correctly
- `tests/` run successfully
- `results/raw/`, `results/aggregated/`, and `figures/` contain the versions you want to publish
- no private local paths, caches, or machine-specific files are accidentally included
