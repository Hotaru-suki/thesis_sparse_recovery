# Experiment Protocol

This protocol follows the current experiment code. If older documents disagree,
use `experiments/*.py`, `configs/*.yaml`, and `results/raw/*.csv` as the source
of truth.

## Execution Entry Points

- `python main.py --exp sparsity`
- `python main.py --exp snr`
- `python main.py --exp runtime`
- `python main.py --exp compression`
- `python main.py --exp matrix_type`
- `python main.py --exp coeff_mode`
- `python main.py --exp ablation`
- `python main.py --exp param_sensitivity`
- `python main.py --all`

CLI overrides supported by all experiment runners:

- `--seed`
- `--trials`
- `--outdir`

## Shared Defaults

`configs/base.yaml` currently defines:

- `m = 96`
- `n = 256`
- `k = 12`
- `matrix_kind = gaussian`
- `coeff_mode = gaussian`
- `group_size = 3`
- `improved_group_size = 2`
- `screening_ratio = 3.0`
- `min_group_size = 1`
- `use_noise_aware_stop = true`
- `use_incremental_solver = true`
- `use_forward_backward = true`
- `min_residual_drop = 0.0001`
- `trials = 30`
- `seed = 20260408`

Individual experiment configs override some of these values. Do not infer a
paper parameter from `base.yaml` alone; check the specific config file.

## Current Experiment Suite

| Experiment | Script | Config | Main sweep variable | Current raw rows | Notes |
| --- | --- | --- | --- | ---: | --- |
| sparsity | `experiments/run_sparsity.py` | `configs/sparsity.yaml` | `k` | 1800 | 10 k values, 30 trials, 3 algorithms, baseline+optimized |
| snr | `experiments/run_snr.py` | `configs/snr.yaml` | `snr_db` | 1920 | 8 SNR values, 30 trials, 4 algorithms, baseline+optimized |
| runtime | `experiments/run_runtime.py` | `configs/runtime.yaml` | `n` | 640 | 4 n values, 20 trials, 4 algorithms, baseline+optimized |
| compression | `experiments/run_compression.py` | `configs/compression.yaml` | `measurement_ratio` | 1280 | 8 ratios, 20 trials, 4 algorithms, baseline+optimized |
| matrix_type | `experiments/run_matrix_type.py` | `configs/matrix_type.yaml` | `matrix_kind` | 360 | 3 matrix types, 20 trials, 3 algorithms, baseline+optimized |
| coeff_mode | `experiments/run_coeff_mode.py` | `configs/coeff_mode.yaml` | `coeff_mode` | 360 | 3 coefficient modes, 20 trials, 3 algorithms, baseline+optimized |
| ablation | `experiments/run_ablation.py` | `configs/ablation.yaml` | `ablation_variant` | 240 | 8 module combinations, 30 trials, optimized only |
| param_sensitivity | `experiments/run_param_sensitivity.py` | `configs/param_sensitivity.yaml` | `screening_ratio`, `group_size` | 200 | Two separate parameter scans, 20 trials per point, optimized only |

Supplementary CSV files are also present, including `ablation_clean.csv`,
`ablation_noise_snr15.csv`, and several `sparsity_clean*.csv` files. Treat them
as thesis-scope supplementary outputs: use them in the main text when they
support the central narrative, otherwise place them in appendix or supplemental
analysis.

## Algorithms and Implementations

Default algorithm construction is in `experiments/common.py`.

- Most sweep experiments include `OMP`, `gOMP`, and `Improved-gOMP`.
- `snr`, `runtime`, and `compression` include `RMP` because their configs set
  `include_rmp: true`.
- Ordinary sweep experiments run both `baseline` and `optimized`
  implementations.
- `ablation` builds named module-combination variants and runs optimized only.
- `param_sensitivity` runs only optimized `Improved-gOMP`.

## Output Layout

- Trial-level outputs: `results/raw/`
- Aggregated summaries: `results/aggregated/`
- Run metadata snapshots: `results/logs/`
- Generated figures: `figures/`
- Text summaries for downstream writing: `deepseek_ready/`

## Reported Metrics

Core metrics exported in the main raw CSV files include:

- `exact_support_recovery`
- `support_recall`
- `support_precision`
- `nmse`
- `relative_l2_error`
- `runtime_sec`
- `iterations`
- `support_size`
- `final_residual_norm`
- `false_positive_count`
- `false_negative_count`
- `solver_time_sec`
- `screening_pool_size_avg`
- `solver_fallback_count`
- `duplicate_candidate_hits`
- `max_support_condition`
- `peak_working_set_bytes`

Timing breakdown files additionally include phase-level runtime columns.
Memory breakdown files additionally include estimated working-set columns.

## Thesis Use Rules

- Use `deepseek_ready/verified_existing_data.md` for the current audit summary.
- Use `deepseek_ready/insertion_plan.md` for the current figure/table plan.
- Use the matching text file under `deepseek_ready/csv_text_summaries/` before
  writing about a CSV.
- Use the matching text file under `deepseek_ready/figure_text_summaries/`
  before writing about a figure.
- Do not cite old parameter counts, old trial counts, or old figure sources from
  previous notes.
