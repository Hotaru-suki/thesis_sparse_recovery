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

Supplementary presets are also present:

- `ablation_clean.yaml`: clean-condition ablation preset
- `sparsity_clean.yaml`, `sparsity_clean_easy.yaml`, `sparsity_clean_hard.yaml`, `sparsity_easy.yaml`, `sparsity_hard.yaml`: supplementary sparsity presets used during result selection

These supplementary presets are not dispatched by `main.py --all` unless a
runner is invoked with `--config <path>`.

## Common Fields

- `m`, `n`, `k`: default problem dimensions
- `matrix_kind`: measurement matrix family
- `coeff_mode`: nonzero coefficient distribution
- `group_size`: baseline `gOMP` group size
- `improved_group_size`: default group size for `Improved-gOMP`
- `screening_ratio`: screening pool multiplier for `Improved-gOMP`
- `improved_screening_ratio`: optional explicit screening-ratio override for `Improved-gOMP`
- `optimized_screening_ratio`: optional optimized-implementation screening-ratio override
- `min_group_size`: lower bound for adaptive group size
- `use_noise_aware_stop`: enables the noise-aware stop rule
- `use_incremental_solver`: enables incremental least-squares solving
- `profile_level`: profiling level used by optimized implementations; `light` trims history/diagnostic memory while preserving final metrics
- `baseline_profile_level`, `optimized_profile_level`: optional per-implementation overrides for benchmark comparisons
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

Run a supplementary preset through an existing runner:

```bash
python -m experiments.run_sparsity --config configs/sparsity_clean_easy.yaml
```

## Notes

- `Improved-gOMP` is configured separately from `gOMP` to keep the baseline comparison explicit.
- The presets are intended for reproducible benchmark runs, not as a stable public API.
- For parameter-sensitivity runs, `experiments/run_param_sensitivity.py` maps
  scanned `group_size` values to `improved_group_size`, and scanned
  `screening_ratio` values to the Improved-gOMP screening override fields.
