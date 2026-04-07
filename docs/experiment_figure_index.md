# 图表索引

| 图名 | 实验脚本 | 聚合 CSV | 横轴 | 纵轴 | 论文拟放置章节 |
| --- | --- | --- | --- | --- | --- |
| `sparsity_exact_support.png` | `experiments/run_sparsity.py` | `results/aggregated/summary_sparsity.csv` | `k` | `exact_support_recovery` | 实验结果与分析 |
| `sparsity_nmse.png` | `experiments/run_sparsity.py` | `results/aggregated/summary_sparsity.csv` | `k` | `nmse` | 实验结果与分析 |
| `sparsity_runtime.png` | `experiments/run_sparsity.py` | `results/aggregated/summary_sparsity.csv` | `k` | `runtime_sec` | 性能优化分析 |
| `snr_nmse.png` | `experiments/run_snr.py` | `results/aggregated/summary_snr.csv` | `snr_db` | `nmse` | 抗噪实验 |
| `snr_support_recall.png` | `experiments/run_snr.py` | `results/aggregated/summary_snr.csv` | `snr_db` | `support_recall` | 抗噪实验 |
| `snr_runtime.png` | `experiments/run_snr.py` | `results/aggregated/summary_snr.csv` | `snr_db` | `runtime_sec` | 抗噪实验 |
| `runtime_compare.png` | `experiments/run_runtime.py` | `results/aggregated/summary_runtime.csv` | `n` | `runtime_sec` | 复杂度与效率 |
| `compression_exact_support.png` | `experiments/run_compression.py` | `results/aggregated/summary_compression.csv` | `measurement_ratio` | `exact_support_recovery` | 压缩率实验 |
| `compression_nmse.png` | `experiments/run_compression.py` | `results/aggregated/summary_compression.csv` | `measurement_ratio` | `nmse` | 压缩率实验 |
| `compression_runtime.png` | `experiments/run_compression.py` | `results/aggregated/summary_compression.csv` | `measurement_ratio` | `runtime_sec` | 压缩率实验 |
| `matrix_type_exact_support.png` | `experiments/run_matrix_type.py` | `results/aggregated/summary_matrix_type.csv` | `matrix_kind` | `exact_support_recovery` | 不同测量矩阵实验 |
| `matrix_type_nmse.png` | `experiments/run_matrix_type.py` | `results/aggregated/summary_matrix_type.csv` | `matrix_kind` | `nmse` | 不同测量矩阵实验 |
| `coeff_mode_exact_support.png` | `experiments/run_coeff_mode.py` | `results/aggregated/summary_coeff_mode.csv` | `coeff_mode` | `exact_support_recovery` | 系数分布实验 |
| `coeff_mode_nmse.png` | `experiments/run_coeff_mode.py` | `results/aggregated/summary_coeff_mode.csv` | `coeff_mode` | `nmse` | 系数分布实验 |
| `coeff_mode_runtime.png` | `experiments/run_coeff_mode.py` | `results/aggregated/summary_coeff_mode.csv` | `coeff_mode` | `runtime_sec` | 系数分布实验 |
| `ablation_runtime.png` | `experiments/run_ablation.py` | `results/aggregated/summary_ablation.csv` | `algorithm` | `runtime_sec` | 消融实验 |
| `ablation_nmse.png` | `experiments/run_ablation.py` | `results/aggregated/summary_ablation.csv` | `algorithm` | `nmse` | 消融实验 |
| `ablation_exact_support.png` | `experiments/run_ablation.py` | `results/aggregated/summary_ablation.csv` | `algorithm` | `exact_support_recovery` | 消融实验 |
| `param_screening_ratio.png` | `experiments/run_param_sensitivity.py` | `results/aggregated/summary_param_sensitivity.csv` | `screening_ratio` | `nmse` | 参数敏感性 |
| `param_group_size.png` | `experiments/run_param_sensitivity.py` | `results/aggregated/summary_param_sensitivity.csv` | `group_size` | `nmse` | 参数敏感性 |
