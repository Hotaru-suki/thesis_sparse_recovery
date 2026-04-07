# Experiment Protocol

## Default Setup

- Core stack: `numpy`, `scipy`, `pandas`, `matplotlib`, `tqdm`
- Default signal dimension: `n = 256`
- Default measurement dimension: `m = 96`
- Default sparsity: `k = 16`
- Default matrix type: `gaussian`
- Default coefficient mode: `gaussian`
- Default `gOMP` group size: `3`
- Default `Improved-gOMP` group size: `2`

## Experiment Suite

- Sparsity sweep: effect of `k` on recovery quality and runtime
- SNR sweep: robustness under changing noise levels
- Runtime sweep: scaling behavior as problem size grows
- Compression sweep: recovery quality under different `m / n`
- Matrix-type sweep: `gaussian`, `bernoulli`, `partial_dct`
- Coefficient-mode sweep: `gaussian`, `rademacher`, `uniform`
- Ablation sweep: impact of screening, solver, and stopping modules
- Parameter sensitivity: `screening_ratio` and group size

## Output Layout

- Trial-level outputs: `results/raw/`
- Aggregated summaries: `results/aggregated/`
- Run metadata and configuration snapshots: `results/logs/`
- Generated figures: `figures/`

## Reported Metrics

- `exact_support_recovery`
- `support_recall`
- `support_precision`
- `nmse`
- `relative_l2_error`
- `runtime_sec`
- `iterations`
- `final_residual_norm`
- `stop_reason`
- `false_positive_count`
- `false_negative_count`
- `solver_time_sec`
- `screening_pool_size_avg`
- `solver_fallback_count`
- `duplicate_candidate_hits`
- `max_support_condition`
- `support_size`
- `rescue_attempted`
- `rescue_accepted`
