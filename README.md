# Sparse Recovery Greedy Algorithms

This repository contains a compact experimental framework for sparse signal recovery with greedy pursuit methods. It focuses on reproducible comparisons between `OMP`, `gOMP`, an engineering-oriented `Improved-gOMP`, and an exploratory `RMP` implementation.

The project is organized as a benchmark-style codebase rather than a general-purpose library. It includes algorithm implementations, experiment runners, aggregated result exports, generated figures, and supporting notes that explain design choices and experiment boundaries.

## Highlights

- Baseline implementations for `OMP` and `gOMP`
- An `Improved-gOMP` variant with modular selection, stopping, and solver strategies
- Sweep scripts for sparsity, SNR, runtime, compression ratio, matrix type, coefficient mode, ablation, and parameter sensitivity
- Saved outputs under `results/raw`, `results/aggregated`, and `figures`
- Unit tests for algorithm behavior and solver correctness

## Repository Layout

```text
thesis_sparse_recovery/
├─ algorithms/
├─ configs/
├─ docs/
├─ experiments/
├─ figures/
├─ results/
│  ├─ aggregated/
│  ├─ logs/
│  └─ raw/
├─ tests/
├─ utils/
├─ main.py
└─ requirements.txt
```

## Environment

Recommended:

- Python 3.10+
- `numpy`
- `scipy`
- `pandas`
- `matplotlib`
- `tqdm`

Install with:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Running Experiments

Run a single sweep:

```bash
python main.py --exp snr
python main.py --exp compression
python main.py --exp ablation
```

Run the full experiment set:

```bash
python main.py --all
```

Optional overrides:

```bash
python main.py --exp snr --seed 20260408 --trials 10 --outdir .
```

## Current Positioning of `Improved-gOMP`

`Improved-gOMP` is designed as a conservative variant of `gOMP`. In the current result set it does not uniformly outperform `OMP` or `gOMP`, and it should not be presented as a universally superior method. Its stronger behavior is concentrated in support precision and false-positive suppression under selected medium-to-high quality measurement regimes.

The public-facing takeaway is therefore:

- `OMP` remains a strong accuracy baseline
- `gOMP` remains the faster group-selection baseline
- `Improved-gOMP` is a tradeoff-oriented variant with more modular recovery logic and better support precision in selected regimes

More detail is documented in [docs/improved_gomp_optimization_note.md](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/docs/improved_gomp_optimization_note.md).

## Key Documents

- [docs/improved_gomp_optimization_note.md](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/docs/improved_gomp_optimization_note.md): design and optimization notes for `Improved-gOMP`
- [docs/experiment_protocol.md](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/docs/experiment_protocol.md): experiment definitions and execution protocol
- [docs/algorithm_boundary.md](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/docs/algorithm_boundary.md): what is baseline reproduction vs. engineering extension
- [docs/source_traceability.md](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/docs/source_traceability.md): source mapping and traceability notes
- [configs/README.md](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/configs/README.md): config presets and common fields
- [results/README.md](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/results/README.md): output layout and artifact naming
- [REPRODUCIBILITY.md](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/REPRODUCIBILITY.md): setup, validation, and rerun steps
- [CONTRIBUTING.md](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/CONTRIBUTING.md): contribution expectations and validation checklist
- [PUBLISHING.md](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/PUBLISHING.md): public release and artifact guidance

## Testing

Run:

```bash
python -m unittest tests.test_algorithms tests.test_config_and_main -q
```

## Notes on Structure

Recent cleanup work separates:

- algorithm configuration mapping in `experiments/common.py`
- solver concerns in `utils/linalg.py`
- selection, rescue, and refinement helpers in `algorithms/improved_gomp.py`

This keeps the experiment layer thinner and makes it easier to expose or disable individual `Improved-gOMP` modules without rewriting the runner pipeline.
