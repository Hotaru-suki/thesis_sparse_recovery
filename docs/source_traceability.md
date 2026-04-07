# Source Traceability

This table records how external references relate to the codebase. The goal is to distinguish direct baseline sources from broader theoretical support and lighter design inspiration.

| Ref. | Year | Title | Relationship | Related Area | In Code | Classification | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [11] | 2016 | Recovery of Sparse Signals via Generalized Orthogonal Matching Pursuit: A New Analysis | Core baseline source | `algorithms/gomp.py` | Yes | Baseline reproduction | Main theoretical anchor for the `gOMP` baseline |
| [13] | 2020 | Preconditioned Generalized Orthogonal Matching Pursuit | Boundary reference | `docs/algorithm_boundary.md` | No | Out-of-scope direction | Used to document a path the repository does not implement |
| [14] | 2024 | Sparse Signal Recovery via Rescaled Matching Pursuit | Exploratory comparison source | `algorithms/rmp.py` | Partial | Exploratory implementation | Kept as an optional comparison route rather than a default benchmark baseline |
| [15] | 2025 | Randomized Orthogonal Matching Pursuit Algorithm with Adaptive Partial Selection for Sparse Signal Recovery | Design inspiration | `algorithms/improved_gomp.py` | Yes | Literature-inspired extension | Motivates adaptive screening, while the concrete logic remains repository-specific |
| [9] | 2015 | Support Recovery with Orthogonal Matching Pursuit in the Presence of Noise | Theoretical support | `algorithms/improved_gomp.py` | No | Theory support | Supports noisy-recovery framing and stopping discussions |
| [10] | 2015 | Sparse Signals Recovery from Noisy Measurements by Orthogonal Matching Pursuit | Theoretical support | `algorithms/improved_gomp.py` | No | Theory support | Supports noisy measurement analysis rather than a direct implementation rule |
| [12] | 2017 | Some New Results about Sufficient Conditions for Exact Support Recovery of Sparse Signals via OMP | Metric support | `utils/metrics.py` | No | Theory support | Relevant to exact-support evaluation context |
| [5] | 2011 | Orthogonal Matching Pursuit for Sparse Signal Recovery with Noise | Background support | `algorithms/omp.py` | No | Theory support | General OMP under noise background |
| [6] | 2011 | Sparse Recovery with Orthogonal Matching Pursuit under RIP | Background support | `algorithms/omp.py` | No | Theory support | General RIP background for OMP-style recovery |
| [7] | 2012 | Generalized Orthogonal Matching Pursuit | Core baseline source | `algorithms/gomp.py` | Yes | Baseline reproduction | Companion source to [11] for the `gOMP` baseline |
| [3] | 2015 | 基于差分的稀疏度自适应重构算法 | Design inspiration | `algorithms/improved_gomp.py` | No | Inspiration | Related to adaptive control ideas rather than direct implementation |
| [4] | 2018 | 压缩感知增强型自适应分段正交匹配追踪算法 | Design inspiration | `algorithms/improved_gomp.py` | No | Inspiration | Relevant to staged/adaptive mechanisms |
| [8] | 2014 | Multipath Matching Pursuit | Boundary reference | `docs/algorithm_boundary.md` | No | Out-of-scope direction | Documents a higher-complexity path excluded from the current repository |
| [1] | 2013 | 信号压缩重构的正交匹配追踪类算法综述 | Background survey | `README.md` | No | General background | Useful for broader context, not tied to a specific implementation |
| [2] | 2014 | 采用正交多项匹配的块稀疏信号重构算法 | Boundary reference | `docs/algorithm_boundary.md` | No | Out-of-scope direction | Documents block-sparse extensions outside the repository scope |
