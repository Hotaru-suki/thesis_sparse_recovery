# Verified Current Data - 当前实验数据审计

生成依据：当前 `experiments/*.py`、`configs/*.yaml` 和 `results/raw/*.csv`。
本文件用于替代旧审计口径；若重新运行实验，需重新生成。

## 实验文件完整性

| 实验 | raw CSV 行数 | aggregated 是否存在 | 变量 | 算法/配置 | implementation |
|---|---:|---|---|---|---|
| sparsity | 1800 | 是 | k=4, 8, 12, 16, 20, 24, 28, 32, 36, 40 | Improved-gOMP, OMP, gOMP | baseline, optimized |
| snr | 1920 | 是 | snr_db=5, 10, 15, 20, 25, 30, 40, clean | Improved-gOMP, OMP, RMP, gOMP | baseline, optimized |
| runtime | 640 | 是 | n=128, 256, 384, 512 | Improved-gOMP, OMP, RMP, gOMP | baseline, optimized |
| compression | 1280 | 是 | measurement_ratio=0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5, 0.5625, 0.625 | Improved-gOMP, OMP, RMP, gOMP | baseline, optimized |
| matrix_type | 360 | 是 | matrix_kind=bernoulli, gaussian, partial_dct | Improved-gOMP, OMP, gOMP | baseline, optimized |
| coeff_mode | 360 | 是 | coeff_mode=gaussian, rademacher, uniform | Improved-gOMP, OMP, gOMP | baseline, optimized |
| ablation | 240 | 是 | ablation_variant=full_suite | Improved-gOMP, gOMP, gOMP+Adaptive+Incremental, gOMP+Adaptive+NoiseAware, gOMP+AdaptiveScreen, gOMP+Incremental+NoiseAware, gOMP+IncrementalSolver, gOMP+NoiseAwareStop | optimized |
| param_sensitivity | 200 | 是 |  | Improved-gOMP | optimized |
| ablation_clean | 240 | 是 | ablation_variant=full_suite | Improved-gOMP, gOMP, gOMP+Adaptive+Incremental, gOMP+Adaptive+NoiseAware, gOMP+AdaptiveScreen, gOMP+Incremental+NoiseAware, gOMP+IncrementalSolver, gOMP+NoiseAwareStop | optimized |
| ablation_noise_snr15 | 240 | 是 | ablation_variant=full_suite | Improved-gOMP, gOMP, gOMP+Adaptive+Incremental, gOMP+Adaptive+NoiseAware, gOMP+AdaptiveScreen, gOMP+Incremental+NoiseAware, gOMP+IncrementalSolver, gOMP+NoiseAwareStop | optimized |
| sparsity_clean | 1800 | 是 | k=4, 8, 12, 16, 20, 24, 28, 32, 36, 40 | Improved-gOMP, OMP, gOMP | baseline, optimized |
| sparsity_clean_easy | 1800 | 是 | k=4, 8, 12, 16, 20, 24, 28, 32, 36, 40 | Improved-gOMP, OMP, gOMP | baseline, optimized |
| sparsity_clean_hard | 1800 | 是 | k=4, 8, 12, 16, 20, 24, 28, 32, 36, 40 | Improved-gOMP, OMP, gOMP | baseline, optimized |
| sparsity_clean_m96 | 1800 | 是 | k=4, 8, 12, 16, 20, 24, 28, 32, 36, 40 | Improved-gOMP, OMP, gOMP | baseline, optimized |

## 关键注意事项

- 当前普通 sweep 多数包含 `baseline` 与 `optimized` 两套 implementation；论文图和结论必须说明采用哪一套。
- 当前 `snr.csv` 包含 8 个 SNR 点：5, 10, 15, 20, 25, 30, 40, clean。
- 当前 `compression.csv` 包含 8 个 measurement_ratio 点：0.1875 到 0.625。
- 当前 `runtime.csv` 为每个 n/algorithm/implementation 20 次试验。
- `param_sensitivity.csv` 中 `screening_ratio` 与 `group_size` 是分开扫描，另一列为空是结构性空值。
- `fallback_reason` 为空通常表示没有 fallback，不是实验失败。

## 论文写作约束

- 每个数字必须追溯到 `results/raw/*.csv` 或 `results/aggregated/*.csv` 的具体列。
- 旧 README、旧 docs、旧 `deepseek_ready` 说明若与当前 CSV 冲突，以当前代码和 CSV 为准。
- clean/easy/m96 等补充图可纳入附录或补充分析，但不得混入主文正式图编号。
