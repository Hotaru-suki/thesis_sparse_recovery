# Sparse Recovery Greedy Algorithms

This repository contains a compact experimental framework for sparse signal recovery with greedy pursuit methods. It focuses on reproducible comparisons between `OMP`, `gOMP`, `Improved-gOMP`, and an exploratory `RMP` implementation, with explicit baseline-vs-optimized implementation benchmarking.

The project is organized as a benchmark-style codebase rather than a general-purpose library. It includes algorithm implementations, experiment runners, aggregated result exports, generated figures, and supporting notes that explain design choices and experiment boundaries.

## Highlights

- Explicit `baseline` and `optimized` implementations for all benchmarked algorithms
- Runtime-breakdown exports for correlation, selection, solve, residual update, and support refinement
- Speedup summaries that compare baseline and optimized implementations per algorithm
- Memory-breakdown and memory-speedup summaries that compare baseline and optimized implementations per algorithm
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

## Current Positioning

The repository is organized around a runtime-first thesis narrative:

- each experimental algorithm exposes a baseline path and an optimized path
- the optimized path prioritizes lower runtime in dominant kernels
- recovery quality is still tracked through NMSE and support metrics so speed-quality tradeoffs remain explicit
- working-memory tradeoffs are exported alongside runtime so memory savings or regressions are explicit rather than implicit

More detail is documented in [docs/improved_gomp_optimization_note.md](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/docs/improved_gomp_optimization_note.md).

## Key Documents

- [docs/improved_gomp_optimization_note.md](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/docs/improved_gomp_optimization_note.md): design and optimization notes for `Improved-gOMP`
- [docs/runtime_memory_balancing_note.md](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/docs/runtime_memory_balancing_note.md): runtime-memory balancing strategy and comparison outputs
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
- implementation-aware benchmarking outputs in `results/raw` and `results/aggregated`

This keeps the experiment layer thinner and makes it easier to expose or disable individual `Improved-gOMP` modules without rewriting the runner pipeline.
