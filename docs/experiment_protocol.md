# 实验协议

## 总体设置

- Python 主栈：`numpy`、`scipy`、`pandas`、`matplotlib`、`tqdm`
- 默认信号维度：`n=256`
- 默认测量维度：`m=96`
- 默认稀疏度：`k=16`
- 默认矩阵：`gaussian`
- 默认系数模式：`gaussian`

## 实验列表

- 稀疏度扫描：考察 `k` 对恢复率、误差和时间的影响
- SNR 扫描：考察噪声水平变化下的稳定性
- 运行时间实验：考察信号维度增长对运行时间的影响
- 压缩率实验：考察测量维度比例 `m/n` 变化下的恢复性能和时间
- 测量矩阵实验：比较 `gaussian`、`bernoulli`、`partial_dct`
- 系数分布实验：比较 `gaussian`、`rademacher`、`uniform`
- 消融实验：拆分 adaptive screening、incremental solver、noise-aware stop
- 参数敏感性实验：考察 `screening_ratio` 与 `group_size`

## 输出规则

- 原始 trial 级数据保存到 `results/raw/`
- 聚合结果保存到 `results/aggregated/`
- 每次运行的配置快照和时间戳保存到 `results/logs/`
- 图表保存到 `figures/`

## 指标

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
