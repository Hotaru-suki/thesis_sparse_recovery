# Insertion Plan - 当前代码口径图表插入计划

生成依据：当前 `results/raw/*.csv` 与 `figures/*.png`。实验范围已锁定为：主实验、补充 clean/noise 实验、参数敏感性实验均尽可能纳入论文；主文空间不足时进入附录或补充分析。

## 主文正式候选图

| 章节 | 编号 | 图片 | 数据来源 | 用途 |
|---|---|---|---|---|
| 4.2 稀疏度实验 | 图4.1 | figures/sparsity_exact_support.png | results/raw/sparsity.csv | 不同 k 下 ESR 对比 |
| 4.2 稀疏度实验 | 图4.2 | figures/sparsity_nmse.png | results/raw/sparsity.csv | 不同 k 下 NMSE 对比 |
| 4.2 稀疏度实验 | 图4.3 | figures/sparsity_runtime.png | results/raw/sparsity.csv | 不同 k 下运行时间对比 |
| 4.3 信噪比实验 | 图4.4 | figures/snr_nmse.png | results/raw/snr.csv | 不同 SNR 下 NMSE 对比 |
| 4.3 信噪比实验 | 图4.5 | figures/snr_support_recall.png | results/raw/snr.csv | 不同 SNR 下支持召回率对比 |
| 4.3 信噪比实验 | 图4.6 | figures/snr_runtime.png | results/raw/snr.csv | 不同 SNR 下运行时间对比 |
| 4.4 运行时间实验 | 图4.7 | figures/runtime_compare.png | results/raw/runtime.csv | baseline 与 optimized 运行时间对比 |
| 4.5 压缩比实验 | 图4.8 | figures/compression_exact_support.png | results/raw/compression.csv | 不同测量比率下 ESR 对比 |
| 4.5 压缩比实验 | 图4.9 | figures/compression_nmse.png | results/raw/compression.csv | 不同测量比率下 NMSE 对比 |
| 4.5 压缩比实验 | 图4.10 | figures/compression_runtime.png | results/raw/compression.csv | 不同测量比率下运行时间对比 |
| 4.6 矩阵类型实验 | 图4.11 | figures/matrix_type_exact_support.png | results/raw/matrix_type.csv | 不同矩阵类型下 ESR 对比 |
| 4.6 矩阵类型实验 | 图4.12 | figures/matrix_type_nmse.png | results/raw/matrix_type.csv | 不同矩阵类型下 NMSE 对比 |
| 4.7 系数分布实验 | 图4.13 | figures/coeff_mode_exact_support.png | results/raw/coeff_mode.csv | 不同系数分布下 ESR 对比 |
| 4.7 系数分布实验 | 图4.14 | figures/coeff_mode_nmse.png | results/raw/coeff_mode.csv | 不同系数分布下 NMSE 对比 |
| 4.7 系数分布实验 | 图4.15 | figures/coeff_mode_runtime.png | results/raw/coeff_mode.csv | 不同系数分布下运行时间对比 |
| 4.8 消融实验 | 图4.16 | figures/ablation_exact_support.png | results/raw/ablation.csv | 模块组合 ESR 对比 |
| 4.8 消融实验 | 图4.17 | figures/ablation_nmse.png | results/raw/ablation.csv | 模块组合 NMSE 对比 |
| 4.8 消融实验 | 图4.18 | figures/ablation_runtime.png | results/raw/ablation.csv | 模块组合运行时间对比 |
| 4.9 参数敏感性 | 图4.19 | figures/param_screening_ratio.png | results/raw/param_sensitivity.csv | screening_ratio 敏感性 |
| 4.9 参数敏感性 | 图4.20 | figures/param_group_size.png | results/raw/param_sensitivity.csv | group_size 敏感性 |

## 补充或附录候选图

以下图片存在于 `figures/`，建议纳入论文附录或正文综合讨论；如需放入正文主图，必须先调整主文图号和正文叙述：

- figures/ablation_clean_exact_support.png
- figures/ablation_clean_nmse.png
- figures/ablation_clean_runtime.png
- figures/ablation_noise_exact_support.png
- figures/ablation_noise_nmse.png
- figures/ablation_noise_runtime.png
- figures/sparsity_clean_exact_support.png
- figures/sparsity_clean_nmse.png
- figures/sparsity_clean_runtime.png
- figures/sparsity_easy_exact_support.png
- figures/sparsity_easy_nmse.png
- figures/sparsity_easy_runtime.png
- figures/sparsity_m96_exact_support.png
- figures/sparsity_m96_nmse.png
- figures/sparsity_m96_runtime.png

## 表格建议

- 表4.1：实验默认参数设置，来源 `configs/*.yaml` 和对应实验入口。
- 表4.2：baseline vs optimized 加速比汇总，来源 `results/aggregated/summary_speedup_*.csv` 或 `results/raw/runtime.csv`。
- 表4.3：消融实验配置说明，来源 `experiments/run_ablation.py`。
- 表4.4：参数敏感性关键结果，来源 `results/raw/param_sensitivity.csv`。

## 全局限制

- 正文中每个数值必须标明可追溯 CSV、列名和筛选条件。
- 图题必须包含关键实验条件，至少包括 m、n、k、SNR 或扫描变量，以及 implementation 口径。
- 如图采用 optimized 数据，正文不能把它描述为 baseline 结果。
- 补充或附录图也必须有正文/附录引用、图题和数据来源。
- 旧文档中与当前 CSV 不一致的 SNR 点、测量比率、trial 数均不得继续使用。
