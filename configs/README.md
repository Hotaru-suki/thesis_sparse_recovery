# Configuration Guide

The `configs/` directory stores experiment presets used by `main.py` and the sweep runners.

## Files

- `base.yaml`: shared default values such as dimensions, sparsity, seed, and output directory
- `sparsity.yaml`: sparsity sweep preset
- `snr.yaml`: SNR sweep preset
- `runtime.yaml`: runtime scaling preset
- `compression.yaml`: measurement-ratio sweep preset
- `matrix_type.yaml`: matrix-family comparison preset
- `coeff_mode.yaml`: coefficient-distribution comparison preset
- `ablation.yaml`: module ablation preset
- `param_sensitivity.yaml`: screening-ratio and group-size sensitivity preset

## Common Fields

- `m`, `n`, `k`: default problem dimensions
- `matrix_kind`: measurement matrix family
- `coeff_mode`: nonzero coefficient distribution
- `group_size`: baseline `gOMP` group size
- `improved_group_size`: default group size for `Improved-gOMP`
- `screening_ratio`: screening pool multiplier for `Improved-gOMP`
- `min_group_size`: lower bound for adaptive group size
- `use_noise_aware_stop`: enables the noise-aware stop rule
- `use_incremental_solver`: enables incremental least-squares solving
- `use_forward_backward`: enables the conservative tail swap module
- `min_residual_drop`: soft-stop threshold
- `trials`: number of trials per sweep point
- `seed`: base random seed
- `outdir`: root output directory

## Usage

Single experiment:

```bash
python main.py --exp snr
```

Override selected values from the CLI:

```bash
python main.py --exp snr --seed 20260408 --trials 10 --outdir .
```

## Notes

- `Improved-gOMP` is configured separately from `gOMP` to keep the baseline comparison explicit.
- The presets are intended for reproducible benchmark runs, not as a stable public API.
