# Codex Prompt — 最终答辩级代码工程交付（稀疏信号恢复中贪婪算法的性能优化实验研究）

你正在为一个本科毕业设计完成**最终答辩级的代码侧工程**。你的任务不是写论文正文，而是完成一个**可复现、可追溯、能直接支撑论文与答辩**的 Python 实验项目。

正式题目固定为：

**《稀疏信号恢复中贪婪算法的性能优化实验研究》**

你必须严格围绕这个题目工作，不能换题，不能把主线改成深度学习、硬件平台优化、RISC-V 汇编优化或通用算法库开发。

---

## 0. 总目标

完成一个最终答辩可用的实验工程，满足以下目标：

1. 实现并验证经典基线算法：**OMP、gOMP**。
2. 至少实现 **1 个近年/近线对照算法**，优先选择：
   - `RMP`（Rescaled Matching Pursuit, 2024）
   - 若实现 RMP 明显困难，可降级为“只做文献级来源映射，不进入代码实现”，但必须在文档中说明原因。
3. 实现本文主方法：**改进 gOMP（improved_gomp）**。
4. 本文主方法必须包含三类改进模块：
   - **自适应候选筛选**
   - **增量正交投影 / 增量最小二乘更新**
   - **噪声感知停止准则**
5. 生成最终答辩级实验产物：
   - 可复现实验脚本
   - 原始与聚合 CSV
   - 论文可用图表 PNG
   - 配置文件
   - 来源映射文档
   - 实验协议文档
   - README 和最终交付检查清单

你必须把项目做成：

> **代码可跑、实验可复现、来源可追踪、边界可答辩。**

---

## 1. 绝对约束（不可违反）

### 1.1 研究边界
你必须保持以下研究主线：

- 研究对象：**稀疏信号恢复中的贪婪算法**
- 主线基线：**OMP / gOMP**
- 主创新落点：**基于 gOMP 框架的性能优化改进**
- 性能优化目标：
  - 运行时间/复杂度
  - 抗噪稳定性
  - 恢复性能与效率的平衡

### 1.2 不能做的事
禁止：

- 引入 PyTorch / TensorFlow / JAX 作为主栈
- 改做深度展开网络或 learned sparse recovery 作为主线
- 改做硬件实现、编译器优化、RISC-V/FPGA/CUDA 主线
- 把项目做成庞大的通用框架
- 只输出几段脚本而没有统一工程结构
- 把所有参考论文都宣称为“直接复现”
- 把本文改进夸大为“全新革命性理论突破”

### 1.3 可使用依赖
仅使用以下依赖完成主工程：

- Python 3.10 / 3.11
- numpy
- scipy
- pandas
- matplotlib
- tqdm
- scikit-learn（仅用于 OMP 结果校验或对照，不可替代核心算法实现）

除非绝对必要，不要引入其他依赖。不要引入需要复杂编译环境的库。

---

## 2. 交付物总清单（最终必须全部存在）

最终工程中必须存在并可用以下内容：

```text
thesis_sparse_recovery/
├─ algorithms/
│  ├─ omp.py
│  ├─ gomp.py
│  ├─ rmp.py                     # 若无法高质量实现，可缺省，但必须在 docs 中说明
│  ├─ improved_gomp.py
│  └─ __init__.py
├─ utils/
│  ├─ data_gen.py
│  ├─ metrics.py
│  ├─ linalg.py
│  ├─ plotting.py
│  ├─ io_utils.py
│  └─ __init__.py
├─ experiments/
│  ├─ run_sparsity.py
│  ├─ run_snr.py
│  ├─ run_runtime.py
│  ├─ run_matrix_type.py
│  ├─ run_ablation.py
│  ├─ run_param_sensitivity.py
│  └─ __init__.py
├─ configs/
│  ├─ base.yaml
│  ├─ sparsity.yaml
│  ├─ snr.yaml
│  ├─ runtime.yaml
│  ├─ matrix_type.yaml
│  ├─ ablation.yaml
│  └─ param_sensitivity.yaml
├─ results/
│  ├─ raw/
│  ├─ aggregated/
│  └─ logs/
├─ figures/
├─ docs/
│  ├─ source_traceability.md
│  ├─ experiment_protocol.md
│  ├─ algorithm_boundary.md
│  ├─ final_delivery_checklist.md
│  └─ experiment_figure_index.md
├─ main.py
├─ requirements.txt
└─ README.md
```

如果仓库里已有部分结构，请在保留现有合理实现的基础上补全，不要无意义重构。

---

## 3. 参考论文覆盖与来源映射要求（非常重要）

### 3.1 总原则
本项目不能只覆盖一两篇文献。必须对参考文献进行**分层覆盖**，并在 `docs/source_traceability.md` 中逐篇说明其关系：

- **核心直接映射**：直接对应基线算法、对照算法或本文改进模块
- **理论支撑**：用于支撑噪声、恢复条件、支持集恢复等理论背景
- **启发映射**：不直接复现，但对本文改进设计有明确启发
- **有限联系**：与本文主线不强绑定，但仍有综述、扩展方向、场景说明意义

### 3.2 必须覆盖的参考文献分层
请在文档中至少覆盖以下 15 篇，并严格给出关系说明。编号沿用论文参考文献编号。

#### A. 核心直接映射（必须在代码或主线文档中明确绑定）
1. **[11] Wang J., Kwon S., Li P., et al. (2016)**  
   *Recovery of Sparse Signals via Generalized Orthogonal Matching Pursuit: A New Analysis*  
   - 作用：`gOMP` 的核心理论/分析来源  
   - 要求：`algorithms/gomp.py`、README、`source_traceability.md` 必须明确绑定该文

2. **[13] Tong Z., Wang F., Hu C., et al. (2020)**  
   *Preconditioned Generalized Orthogonal Matching Pursuit*  
   - 作用：gOMP 优化路线的重要代表  
   - 要求：至少进入文献映射和算法边界说明；若不实现，必须说明为何本文不采用预处理路线

3. **[14] Li W., Ye P. (2024)**  
   *Sparse Signal Recovery via Rescaled Matching Pursuit*  
   - 作用：近年的低复杂度优化路线代表  
   - 要求：优先作为近年对照算法实现 `rmp.py`；如无法高质量实现，则在文档中说明有限实现或未实现原因

4. **[15] Wen J., Li C., Shu Q., et al. (2025)**  
   *Randomized Orthogonal Matching Pursuit Algorithm with Adaptive Partial Selection for Sparse Signal Recovery*  
   - 作用：本文“自适应候选筛选”模块的最关键近年来源  
   - 要求：`improved_gomp.py` 中的候选筛选设计必须在注释和文档里说明“受该类思路启发，但具体规则由本文工程设计实现”

#### B. 理论支撑（必须进入论文支撑文档和实验设计说明）
5. **[9] Wang J. (2015)**  
   *Support Recovery with Orthogonal Matching Pursuit in the Presence of Noise*  
   - 作用：噪声环境下支撑恢复分析  
   - 要求：支撑 SNR 实验设计与 noise-aware stopping 的必要性

6. **[10] Shen Y., Li S. (2015)**  
   *Sparse Signals Recovery from Noisy Measurements by Orthogonal Matching Pursuit*  
   - 作用：noisy measurements 下 OMP 恢复分析  
   - 要求：支撑 SNR 相关实验和抗噪评价指标

7. **[12] Liu C., Fang Y., Liu J. (2017)**  
   *Some New Results about Sufficient Conditions for Exact Support Recovery of Sparse Signals via OMP*  
   - 作用：支持集恢复条件的理论补充  
   - 要求：支撑 exact support recovery / support recall 指标的理论背景说明

8. **[5] Cai T. T., Wang L. (2011)**  
   *Orthogonal Matching Pursuit for Sparse Signal Recovery with Noise*  
   - 作用：OMP 噪声理论基础  
   - 要求：作为基础理论支撑

9. **[6] Zhang T. (2011)**  
   *Sparse Recovery with Orthogonal Matching Pursuit under RIP*  
   - 作用：OMP 的 RIP 条件背景  
   - 要求：作为基础理论支撑

10. **[7] Wang J., Kwon S., Shim B. (2012)**  
    *Generalized Orthogonal Matching Pursuit*  
    - 作用：gOMP 的方法起源之一  
    - 要求：与 [11] 共同组成 gOMP 背景链条；[7] 偏方法提出，[11] 偏新分析

#### C. 启发映射（必须说明启发点，但不要伪装成直接复现）
11. **[3] 张凤珍等 (2015)**  
    *基于差分的稀疏度自适应重构算法*  
    - 作用：对自适应稀疏度、停止准则、动态参数选择提供启发

12. **[4] 何雪云等 (2018)**  
    *压缩感知增强型自适应分段正交匹配追踪算法*  
    - 作用：对“分阶段/分段/自适应机制”提供启发

13. **[8] Kwon S., Wang J., Shim B. (2014)**  
    *Multipath Matching Pursuit*  
    - 作用：说明另一条提升恢复性能的路线是扩大搜索路径，但复杂度更高；本文不走该路线，而走轻量筛选+增量求解路线

#### D. 有限联系（必须说明有限联系，而不是忽略）
14. **[1] 杨真真等 (2013)**  
    *信号压缩重构的正交匹配追踪类算法综述*  
    - 作用：综述与国内研究脉络，不作为具体模块直接来源

15. **[2] 徐燕，邱晓晖 (2014)**  
    *采用正交多项匹配的块稀疏信号重构算法*  
    - 作用：块稀疏/结构化稀疏扩展方向说明；本文不做块稀疏主线，但需说明其有限联系

### 3.3 强制文档要求
你必须生成 `docs/source_traceability.md`，表格字段至少包括：

- 参考文献编号
- 年份
- 标题
- 关系层级（核心 / 支撑 / 启发 / 有限）
- 关联的算法模块
- 关联的论文章节（用拟定章节名即可）
- 是否进入代码实现
- 若未进入实现，有限联系/启发意义是什么
- 如果进入实现，是“文献复现 / 文献启发下改造 / 本文新增工程设计”中的哪一类

---

## 4. 算法边界与实现要求

### 4.1 基线一：OMP
实现标准 OMP。

建议接口：

```python

def omp(Phi, y, k=None, tol=None, max_iter=None, return_info=True):
    ...
```

要求：
- 不要用 `pinv` 作为主路径
- 用 `numpy.linalg.lstsq` 或更稳的线性代数流程
- 返回：
  - `x_hat`
  - `support`
  - `info`
- `info` 至少包含：
  - `iterations`
  - `runtime_sec`
  - `residual_history`
  - `support_history`
  - `stop_reason`

### 4.2 基线二：gOMP
实现 gOMP。

建议接口：

```python

def gomp(Phi, y, group_size=2, k=None, tol=None, max_iter=None, return_info=True):
    ...
```

要求：
- 每轮选择多个原子
- 正确处理 support 去重
- 求解过程稳定
- `info` 字段同 OMP
- 在文档和注释中标出与 [7][11] 的关系

### 4.3 近年对照：RMP（优先）
优先尝试实现 `rmp.py`，并在文档中说明与 [14] 的对应关系。

要求：
- 若实现高质量版本，则进入正式实验对比
- 若实现质量不足以进入正式对比：
  - 可以保留为 `experimental_rmp`
  - 但必须在 README 和 `source_traceability.md` 中说明边界

### 4.4 本文主方法：improved_gomp
这是重点。

建议接口：

```python

def improved_gomp(
    Phi,
    y,
    group_size=2,
    k=None,
    tol=None,
    max_iter=None,
    screening_ratio=3.0,
    min_group_size=1,
    use_noise_aware_stop=True,
    use_incremental_solver=True,
    noise_sigma=None,
    return_info=True,
):
    ...
```

必须包含三部分：

#### 模块 A：自适应候选筛选
要求：
- 不能把“自适应”写成固定常数
- 每轮先计算相关性 `corr = abs(Phi.T @ residual)`
- 动态确定候选池大小 `L_t`
- 可基于以下任一或组合因素：
  - 当前残差范数
  - 前后轮残差下降幅度
  - 相关性分布（如前若干大值的衰减趋势）
  - 当前迭代轮数
- 允许策略：top-L 后再 re-ranking
- 必须在代码注释中说明：
  - 与 [15] 的关系属于“文献启发下的工程化设计”
  - 不是对 [15] 的逐行复现

#### 模块 B：增量正交投影 / 增量求解
要求优先级：
1. Cholesky 增量更新
2. QR 增量更新
3. Gram 小系统缓存 + 稳定求解 + fallback

最低要求：
- 不要每轮都完整重算支持集最小二乘作为唯一主路径
- 必须维护缓存结构，例如：
  - `G = Phi_S^T Phi_S`
  - `b = Phi_S^T y`
  - Cholesky / QR 因子
- support 扩展时增量更新缓存
- `info` 中记录：
  - 是否使用增量求解
  - 每轮求解时间
  - 每轮 support size

这部分要在文档中明确写成：
- **本文在 gOMP 框架下的实现性/工程性优化设计**
- 可以受快速投影/快速回归类方法启发，但不要伪装成某一篇参考文献的直接原样复现

#### 模块 C：噪声感知停止准则
至少实现：
- 残差范数阈值停止
- 连续两轮残差改进幅度过小停止

进一步建议：
- 当给定 `noise_sigma` 时，支持 `||r||_2^2 <= c * m * sigma^2` 类准则

要求：
- 不允许只按固定迭代次数停止
- 必须支持开关，供消融实验使用
- 在文档中说明与 [9][10] 的关系：这些文献支撑抗噪场景的重要性，但本文停止规则属于本文设计

---

## 5. 文档中必须写清楚的“边界口径”

请生成 `docs/algorithm_boundary.md`，明确说明：

### 5.1 哪些是文献复现
例如：
- OMP（经典基线）
- gOMP（依据 [7][11]）
- RMP（如实现，则依据 [14]）

### 5.2 哪些是文献启发下的改造
例如：
- 自适应候选筛选（受 [15] 启发）
- 自适应停止（受 [3][4][9][10] 问题意识启发）

### 5.3 哪些是本文新增的工程设计
例如：
- 增量缓存组织
- fallback 策略
- 统一实验 IO 结构
- 消融实验配置
- 结果汇总与可追溯脚本

这个文档的目的是让后续论文和答辩能明确区分：
- 复现
- 启发
- 本文新增

---

## 6. 数据生成与实验模型要求

### 6.1 信号生成
实现：

```python

def generate_sparse_signal(n, k, coeff_mode="gaussian", normalized=False, rng=None):
    ...
```

要求：
- 随机产生 k-稀疏信号
- 支持至少两种系数模式：
  - `gaussian`
  - `rademacher` 或 `uniform`
- 返回真实 support

### 6.2 测量矩阵
实现：

```python

def generate_measurement_matrix(m, n, kind="gaussian", normalize_columns=True, rng=None):
    ...
```

至少支持：
- `gaussian`
- `bernoulli`
- `partial_dct`（优先实现；如果时间有限，也要在 TODO 文档中说明）
- 可选：`correlated_gaussian`

要求：
- 默认列归一化
- 支持固定随机种子

### 6.3 噪声模型
实现：

```python

def add_noise(y_clean, snr_db=None, sigma=None, rng=None):
    ...
```

要求：
- 支持按 `snr_db` 加噪
- 返回 noisy measurement 和噪声水平估计值/真实值

---

## 7. 指标体系（最终论文级）

必须实现并统一保存以下指标：

- `exact_support_recovery`：是否完全恢复真实支持集
- `support_recall`
- `support_precision`
- `nmse`
- `relative_l2_error`
- `runtime_sec`
- `iterations`
- `final_residual_norm`
- `stop_reason`

建议额外保存：
- `false_positive_count`
- `false_negative_count`
- `solver_time_sec`
- `screening_pool_size_avg`

这些指标必须能进入 CSV。

---

## 8. 实验项目要求（最终答辩级）

你必须完成以下实验，并全部产出原始和聚合结果。

### 8.1 稀疏度扫描实验
脚本：`experiments/run_sparsity.py`

目的：比较稀疏度变化下的恢复成功率、误差与运行时间。

建议默认参数：
- `n = 256`
- `m = 96`
- `k_list = [4, 8, 12, ..., 40]`
- `trials >= 30`（正式版建议 50）

输出：
- `results/raw/sparsity_*.csv`
- `results/aggregated/summary_sparsity.csv`
- 图：
  - `figures/sparsity_exact_support.png`
  - `figures/sparsity_nmse.png`
  - `figures/sparsity_runtime.png`

### 8.2 SNR 扫描实验
脚本：`experiments/run_snr.py`

目的：比较不同噪声水平下的恢复稳定性。

建议默认参数：
- `snr_db in [5, 10, 15, 20, 30, None(clean)]`
- 固定 `n, m, k`
- `trials >= 30`

输出：
- `results/raw/snr_*.csv`
- `results/aggregated/summary_snr.csv`
- 图：
  - `figures/snr_nmse.png`
  - `figures/snr_support_recall.png`
  - `figures/snr_runtime.png`

### 8.3 运行时间实验
脚本：`experiments/run_runtime.py`

目的：突出“性能优化”主线。

至少考察：
- runtime vs sparsity
- runtime vs signal dimension
- 可选：runtime vs measurement dimension

输出：
- `results/aggregated/summary_runtime.csv`
- 图：`figures/runtime_compare.png`

### 8.4 测量矩阵类型实验
脚本：`experiments/run_matrix_type.py`

至少比较：
- Gaussian
- Bernoulli
- Partial DCT（若已实现）
- 可选：Correlated Gaussian

输出：
- `results/aggregated/summary_matrix_type.csv`
- 图：
  - `figures/matrix_type_exact_support.png`
  - `figures/matrix_type_nmse.png`

### 8.5 消融实验
脚本：`experiments/run_ablation.py`

必须拆开比较：
- 基线 gOMP
- gOMP + 自适应候选筛选
- gOMP + 增量求解
- gOMP + 噪声感知停止
- 完整 improved_gomp

输出：
- `results/aggregated/summary_ablation.csv`
- 图：
  - `figures/ablation_runtime.png`
  - `figures/ablation_nmse.png`
  - `figures/ablation_exact_support.png`

### 8.6 参数敏感性实验
脚本：`experiments/run_param_sensitivity.py`

至少考察：
- `screening_ratio`
- `group_size`
- 停止阈值相关参数

输出：
- `results/aggregated/summary_param_sensitivity.csv`
- 图：
  - `figures/param_screening_ratio.png`
  - `figures/param_group_size.png`

---

## 9. 可追溯输出要求（必须做到）

### 9.1 原始与聚合数据分离
所有实验必须同时输出：
- 原始 trial 级结果：`results/raw/*.csv`
- 聚合结果：`results/aggregated/*.csv`

### 9.2 每张图可追溯
生成 `docs/experiment_figure_index.md`，至少记录：
- 图名
- 对应实验脚本
- 对应聚合 CSV
- 主要横轴/纵轴
- 论文拟放置章节

### 9.3 配置可追溯
每次正式实验运行时：
- 将使用的配置复制或保存到 `results/logs/`
- 写入时间戳和随机种子

### 9.4 统一日志
至少记录：
- 运行时间
- 使用的算法列表
- trials 数
- 关键参数
- 是否成功完成

---

## 10. README 要求

README 必须写清：

1. 项目是什么，正式题目是什么
2. 本项目研究主线是什么
3. 已实现哪些算法
4. 哪些算法是：
   - 文献复现
   - 文献启发下改造
   - 本文新增工程设计
5. 如何安装依赖
6. 如何运行单个实验
7. 如何一键运行全部正式实验
8. 结果会输出到哪里
9. `docs/source_traceability.md` 和 `docs/algorithm_boundary.md` 在哪里
10. 当前已知限制

---

## 11. 主程序入口要求

`main.py` 至少支持以下命令风格：

```bash
python main.py --all
python main.py --exp sparsity
python main.py --exp snr
python main.py --exp runtime
python main.py --exp matrix_type
python main.py --exp ablation
python main.py --exp param_sensitivity
```

要求：
- 默认读取 `configs/` 中对应配置
- 支持 `--seed`
- 支持 `--trials`
- 支持 `--outdir`
- 控制台输出清晰

---

## 12. 代码质量要求

### 12.1 代码风格
- 模块化
- 有类型注释（适度即可，不必过度）
- 关键函数有 docstring
- 不要写魔法数字
- 算法参数集中管理

### 12.2 稳定性
- 合理处理空 support、重复支持集、奇异矩阵等问题
- 在数值问题出现时优雅 fallback
- 记录 stop_reason 和 fallback_reason

### 12.3 不要过度工程化
- 不要引入复杂 class hierarchy，除非显著提升清晰度
- 优先清楚的函数式实现

---

## 13. 最终验收标准（必须逐条满足）

你完成后，必须确保以下项目全部满足：

### 13.1 算法层
- [ ] OMP 可用
- [ ] gOMP 可用
- [ ] improved_gomp 可用
- [ ] RMP 已实现，或已在文档中说明为何不进入实现

### 13.2 实验层
- [ ] 稀疏度实验可跑
- [ ] SNR 实验可跑
- [ ] 运行时间实验可跑
- [ ] 测量矩阵实验可跑
- [ ] 消融实验可跑
- [ ] 参数敏感性实验可跑

### 13.3 数据层
- [ ] 原始 trial 数据保存
- [ ] 聚合数据保存
- [ ] 所有论文图对应 CSV 可追溯

### 13.4 文档层
- [ ] `README.md`
- [ ] `docs/source_traceability.md`
- [ ] `docs/algorithm_boundary.md`
- [ ] `docs/experiment_protocol.md`
- [ ] `docs/experiment_figure_index.md`
- [ ] `docs/final_delivery_checklist.md`

### 13.5 边界层
- [ ] 清楚区分复现 / 启发 / 本文新增
- [ ] 对所有参考文献给出关系说明
- [ ] 对未实现但重要的论文说明“有限联系”或“不进入实现的理由”

---

## 14. 建议执行顺序（必须务实）

请按以下顺序推进，不要一开始就堆所有实验：

1. 修复并统一 `OMP / gOMP` 接口
2. 建立数据生成、指标计算、IO 与 plotting 工具
3. 完成 `improved_gomp` 第一版
4. 跑最小实验检查框架正确性
5. 完成正式实验脚本
6. 生成 docs 文档
7. 统一 README 与主入口
8. 最后检查全部输出物是否齐全

---

## 15. 你完成后必须给出的最终说明

在最终提交中，请额外给出一段简短总结，说明：

1. 已实现哪些算法
2. 哪些文献进入了直接实现映射
3. 哪些文献只作为启发或支撑
4. `improved_gomp` 的三大模块分别对应什么来源边界
5. 当前工程还剩哪些局限

注意：
这段总结要**诚实、克制、边界清晰**，不能把工程性优化说成理论突破。

---

## 16. 最重要的提醒

你不是在做“能跑就行”的教学 demo，也不是在堆砌论文名词。你的目标是交付一个：

> **能支撑最终论文写作与答辩追问的代码工程。**

因此，最终判断标准不是“是否有几个 py 文件”，而是：

- 代码是否真的可跑
- 图表是否真的可复现
- 文献关系是否真的可追溯
- 创新边界是否真的说得清

如果某项实现做不到高质量，请：
- 降级其角色
- 在文档里明确写清边界
- 不要假装已经完成

这是允许的；虚构和混淆是不允许的。
