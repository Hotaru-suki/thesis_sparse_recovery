# 来源映射

| 编号 | 年份 | 标题 | 关系层级 | 关联算法模块 | 关联章节 | 是否进入代码实现 | 实现归类 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [11] | 2016 | Recovery of Sparse Signals via Generalized Orthogonal Matching Pursuit: A New Analysis | 核心 | `algorithms/gomp.py` | gOMP 基线 | 是 | 文献复现 | 作为 gOMP 理论分析主绑定来源 |
| [13] | 2020 | Preconditioned Generalized Orthogonal Matching Pursuit | 核心 | `docs/algorithm_boundary.md` | 优化路线对比 | 否 | 有限联系 | 说明预处理路线存在，但本文不采用该主线 |
| [14] | 2024 | Sparse Signal Recovery via Rescaled Matching Pursuit | 核心 | `algorithms/rmp.py` | 近年算法对照边界 | 部分 | 文献启发下改造 | 保留探索性实现，不进入默认正式实验 |
| [15] | 2025 | Randomized Orthogonal Matching Pursuit Algorithm with Adaptive Partial Selection for Sparse Signal Recovery | 核心 | `algorithms/improved_gomp.py` | 改进方法设计 | 是 | 文献启发下改造 | 自适应候选筛选受其启发，具体规则为本文工程设计 |
| [9] | 2015 | Support Recovery with Orthogonal Matching Pursuit in the Presence of Noise | 支撑 | `algorithms/improved_gomp.py` | 抗噪停止准则 | 否 | 理论支撑 | 支撑 SNR 实验和噪声感知停止的必要性 |
| [10] | 2015 | Sparse Signals Recovery from Noisy Measurements by Orthogonal Matching Pursuit | 支撑 | `algorithms/improved_gomp.py` | 抗噪停止准则 | 否 | 理论支撑 | 支撑 noisy measurement 背景与评价指标 |
| [12] | 2017 | Some New Results about Sufficient Conditions for Exact Support Recovery of Sparse Signals via OMP | 支撑 | `utils/metrics.py` | 指标设计 | 否 | 理论支撑 | 支撑 exact support recovery 指标背景 |
| [5] | 2011 | Orthogonal Matching Pursuit for Sparse Signal Recovery with Noise | 支撑 | `algorithms/omp.py` | OMP 理论基础 | 否 | 理论支撑 | 提供 OMP 噪声环境基础 |
| [6] | 2011 | Sparse Recovery with Orthogonal Matching Pursuit under RIP | 支撑 | `algorithms/omp.py` | OMP 理论基础 | 否 | 理论支撑 | 作为 RIP 背景说明 |
| [7] | 2012 | Generalized Orthogonal Matching Pursuit | 支撑 | `algorithms/gomp.py` | gOMP 方法来源 | 是 | 文献复现 | 与 [11] 共同构成 gOMP 背景链条 |
| [3] | 2015 | 基于差分的稀疏度自适应重构算法 | 启发 | `algorithms/improved_gomp.py` | 自适应参数与停止 | 否 | 启发映射 | 提供动态参数与停止意识，不做直接复现 |
| [4] | 2018 | 压缩感知增强型自适应分段正交匹配追踪算法 | 启发 | `algorithms/improved_gomp.py` | 分阶段机制 | 否 | 启发映射 | 提供阶段化、自适应机制启发 |
| [8] | 2014 | Multipath Matching Pursuit | 启发 | `docs/algorithm_boundary.md` | 路线边界说明 | 否 | 启发映射 | 作为高复杂度提升路线对照，本文不采用 |
| [1] | 2013 | 信号压缩重构的正交匹配追踪类算法综述 | 有限 | `README.md` | 研究背景 | 否 | 有限联系 | 用于综述与研究脉络，不直接绑定实现 |
| [2] | 2014 | 采用正交多项匹配的块稀疏信号重构算法 | 有限 | `docs/algorithm_boundary.md` | 扩展方向 | 否 | 有限联系 | 作为块稀疏扩展方向说明，不进入本文主线 |
