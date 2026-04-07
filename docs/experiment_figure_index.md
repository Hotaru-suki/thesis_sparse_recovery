# Figure Index

| Figure | Script | Aggregated CSV | X Axis | Y Axis | Suggested Use |
| --- | --- | --- | --- | --- | --- |
| `sparsity_exact_support.png` | `experiments/run_sparsity.py` | `results/aggregated/summary_sparsity.csv` | `k` | `exact_support_recovery` | sparsity-recovery comparison |
| `sparsity_nmse.png` | `experiments/run_sparsity.py` | `results/aggregated/summary_sparsity.csv` | `k` | `nmse` | sparsity-error comparison |
| `sparsity_runtime.png` | `experiments/run_sparsity.py` | `results/aggregated/summary_sparsity.csv` | `k` | `runtime_sec` | sparsity-runtime comparison |
| `snr_nmse.png` | `experiments/run_snr.py` | `results/aggregated/summary_snr.csv` | `snr_db` | `nmse` | noise robustness analysis |
| `snr_support_recall.png` | `experiments/run_snr.py` | `results/aggregated/summary_snr.csv` | `snr_db` | `support_recall` | support recall under noise |
| `snr_runtime.png` | `experiments/run_snr.py` | `results/aggregated/summary_snr.csv` | `snr_db` | `runtime_sec` | runtime under noise |
| `runtime_compare.png` | `experiments/run_runtime.py` | `results/aggregated/summary_runtime.csv` | `n` | `runtime_sec` | scaling and runtime comparison |
| `compression_exact_support.png` | `experiments/run_compression.py` | `results/aggregated/summary_compression.csv` | `measurement_ratio` | `exact_support_recovery` | compression-recovery comparison |
| `compression_nmse.png` | `experiments/run_compression.py` | `results/aggregated/summary_compression.csv` | `measurement_ratio` | `nmse` | compression-error comparison |
| `compression_runtime.png` | `experiments/run_compression.py` | `results/aggregated/summary_compression.csv` | `measurement_ratio` | `runtime_sec` | compression-runtime comparison |
| `matrix_type_exact_support.png` | `experiments/run_matrix_type.py` | `results/aggregated/summary_matrix_type.csv` | `matrix_kind` | `exact_support_recovery` | matrix-type recovery comparison |
| `matrix_type_nmse.png` | `experiments/run_matrix_type.py` | `results/aggregated/summary_matrix_type.csv` | `matrix_kind` | `nmse` | matrix-type error comparison |
| `coeff_mode_exact_support.png` | `experiments/run_coeff_mode.py` | `results/aggregated/summary_coeff_mode.csv` | `coeff_mode` | `exact_support_recovery` | coefficient-mode recovery comparison |
| `coeff_mode_nmse.png` | `experiments/run_coeff_mode.py` | `results/aggregated/summary_coeff_mode.csv` | `coeff_mode` | `nmse` | coefficient-mode error comparison |
| `coeff_mode_runtime.png` | `experiments/run_coeff_mode.py` | `results/aggregated/summary_coeff_mode.csv` | `coeff_mode` | `runtime_sec` | coefficient-mode runtime comparison |
| `ablation_runtime.png` | `experiments/run_ablation.py` | `results/aggregated/summary_ablation.csv` | `algorithm` | `runtime_sec` | module ablation runtime |
| `ablation_nmse.png` | `experiments/run_ablation.py` | `results/aggregated/summary_ablation.csv` | `algorithm` | `nmse` | module ablation error |
| `ablation_exact_support.png` | `experiments/run_ablation.py` | `results/aggregated/summary_ablation.csv` | `algorithm` | `exact_support_recovery` | module ablation recovery |
| `param_screening_ratio.png` | `experiments/run_param_sensitivity.py` | `results/aggregated/summary_param_sensitivity.csv` | `screening_ratio` | `nmse` | screening-ratio sensitivity |
| `param_group_size.png` | `experiments/run_param_sensitivity.py` | `results/aggregated/summary_param_sensitivity.csv` | `group_size` | `nmse` | group-size sensitivity |
