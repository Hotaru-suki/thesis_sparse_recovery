# Experiment Figure Index

This index follows the current experiment code and CSV outputs. If it conflicts
with older README or thesis notes, use `experiments/*.py`, `configs/*.yaml`, and
`results/raw/*.csv` as the source of truth.

## Main-Text Candidate Figures

| Figure | Script | Raw CSV | Aggregated CSV | X Axis | Y Axis | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `sparsity_exact_support.png` | `experiments/run_sparsity.py` | `results/raw/sparsity.csv` | `results/aggregated/summary_sparsity.csv` | `k` | `exact_support_recovery` | Use optimized implementation unless explicitly comparing implementations. |
| `sparsity_nmse.png` | `experiments/run_sparsity.py` | `results/raw/sparsity.csv` | `results/aggregated/summary_sparsity.csv` | `k` | `nmse` | Same sparsity setting as the ESR figure. |
| `sparsity_runtime.png` | `experiments/run_sparsity.py` | `results/raw/sparsity.csv` | `results/aggregated/summary_sparsity.csv` | `k` | `runtime_sec` | Runtime should state implementation. |
| `snr_nmse.png` | `experiments/run_snr.py` | `results/raw/snr.csv` | `results/aggregated/summary_snr.csv` | `snr_db` | `nmse` | Current SNR values: 5, 10, 15, 20, 25, 30, 40, clean. |
| `snr_support_recall.png` | `experiments/run_snr.py` | `results/raw/snr.csv` | `results/aggregated/summary_snr.csv` | `snr_db` | `support_recall` | Includes RMP. |
| `snr_runtime.png` | `experiments/run_snr.py` | `results/raw/snr.csv` | `results/aggregated/summary_snr.csv` | `snr_db` | `runtime_sec` | Includes baseline and optimized in CSV. |
| `runtime_compare.png` | `experiments/run_runtime.py` | `results/raw/runtime.csv` | `results/aggregated/summary_runtime.csv` | `n` | `runtime_sec` | Current runtime CSV has 20 trials per n/algorithm/implementation group. |
| `compression_exact_support.png` | `experiments/run_compression.py` | `results/raw/compression.csv` | `results/aggregated/summary_compression.csv` | `measurement_ratio` | `exact_support_recovery` | Current ratios: 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5, 0.5625, 0.625. |
| `compression_nmse.png` | `experiments/run_compression.py` | `results/raw/compression.csv` | `results/aggregated/summary_compression.csv` | `measurement_ratio` | `nmse` | Same compression setting as ESR figure. |
| `compression_runtime.png` | `experiments/run_compression.py` | `results/raw/compression.csv` | `results/aggregated/summary_compression.csv` | `measurement_ratio` | `runtime_sec` | Runtime should state implementation. |
| `matrix_type_exact_support.png` | `experiments/run_matrix_type.py` | `results/raw/matrix_type.csv` | `results/aggregated/summary_matrix_type.csv` | `matrix_kind` | `exact_support_recovery` | Current matrix types: gaussian, bernoulli, partial_dct. |
| `matrix_type_nmse.png` | `experiments/run_matrix_type.py` | `results/raw/matrix_type.csv` | `results/aggregated/summary_matrix_type.csv` | `matrix_kind` | `nmse` | Matrix-type experiment does not include RMP. |
| `coeff_mode_exact_support.png` | `experiments/run_coeff_mode.py` | `results/raw/coeff_mode.csv` | `results/aggregated/summary_coeff_mode.csv` | `coeff_mode` | `exact_support_recovery` | Current coefficient modes: gaussian, rademacher, uniform. |
| `coeff_mode_nmse.png` | `experiments/run_coeff_mode.py` | `results/raw/coeff_mode.csv` | `results/aggregated/summary_coeff_mode.csv` | `coeff_mode` | `nmse` | Coefficient-mode experiment does not include RMP. |
| `coeff_mode_runtime.png` | `experiments/run_coeff_mode.py` | `results/raw/coeff_mode.csv` | `results/aggregated/summary_coeff_mode.csv` | `coeff_mode` | `runtime_sec` | Runtime should state implementation. |
| `ablation_exact_support.png` | `experiments/run_ablation.py` | `results/raw/ablation.csv` | `results/aggregated/summary_ablation.csv` | `algorithm` | `exact_support_recovery` | Ablation CSV contains optimized implementation only. |
| `ablation_nmse.png` | `experiments/run_ablation.py` | `results/raw/ablation.csv` | `results/aggregated/summary_ablation.csv` | `algorithm` | `nmse` | Algorithm names are module combinations. |
| `ablation_runtime.png` | `experiments/run_ablation.py` | `results/raw/ablation.csv` | `results/aggregated/summary_ablation.csv` | `algorithm` | `runtime_sec` | Use for module runtime comparison. |
| `param_screening_ratio.png` | `experiments/run_param_sensitivity.py` | `results/raw/param_sensitivity.csv` | `results/aggregated/summary_param_sensitivity.csv` | `screening_ratio` | `nmse` | `group_size` is structurally empty for this half of the scan. |
| `param_group_size.png` | `experiments/run_param_sensitivity.py` | `results/raw/param_sensitivity.csv` | `results/aggregated/summary_param_sensitivity.csv` | `group_size` | `nmse` | `screening_ratio` is structurally empty for this half of the scan. |

## Appendix or Supplementary Candidate Figures

The following files exist under `figures/` and should be included where
possible as appendix or supplementary analysis figures. If any of them move into
the main text, update the figure numbering and insertion plan first:

- `ablation_clean_exact_support.png`
- `ablation_clean_nmse.png`
- `ablation_clean_runtime.png`
- `ablation_noise_exact_support.png`
- `ablation_noise_nmse.png`
- `ablation_noise_runtime.png`
- `sparsity_easy_exact_support.png`
- `sparsity_easy_nmse.png`
- `sparsity_easy_runtime.png`
- `sparsity_exact_support_backup.png`
- `sparsity_m96_exact_support.png`
- `sparsity_m96_nmse.png`
- `sparsity_m96_runtime.png`
- `sparsity_nmse_backup.png`
- `sparsity_runtime_backup.png`

## Traceability Rules

- Every figure used in the thesis must have a matching text explanation in
  `deepseek_ready/figure_text_summaries/`.
- Every CSV used in the thesis must have a matching summary in
  `deepseek_ready/csv_text_summaries/`.
- Do not cite old SNR point counts, old compression-ratio counts, or old runtime
  trial counts. Use the current raw CSV files.
