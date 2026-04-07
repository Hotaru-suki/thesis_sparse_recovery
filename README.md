# 稀疏信号恢复中贪婪算法的性能优化实验研究

本项目是本科毕业设计 **《稀疏信号恢复中贪婪算法的性能优化实验研究》** 的最终答辩级 Python 实验工程。工程目标不是构建通用算法框架，而是围绕稀疏信号恢复中的贪婪算法，交付一套 **可运行、可复现、可追溯、可直接支撑论文与答辩** 的实验项目。

## 研究主线

- 研究对象：稀疏信号恢复中的贪婪算法
- 基线算法：`OMP`、`gOMP`
- 近年对照：`rmp` 的边界受控探索性实现
- 主方法：`improved_gomp`
- 优化目标：恢复性能、抗噪稳定性与运行效率之间的平衡

`improved_gomp` 当前包含三类核心改进模块：

- 自适应候选筛选
- 增量 Gram 缓存 / 增量最小二乘求解
- 噪声感知停止准则

## 已实现算法与归类

### 文献复现

- `OMP`：经典基线实现
- `gOMP`：对应 [7][11] 的基线链条实现

### 文献启发下改造

- `improved_gomp`：自适应候选筛选受 [15] 启发，噪声感知停止受 [9][10] 的问题意识支撑，但具体规则为本文工程化设计
- `rmp`：参考 [14] 提供探索性实现，用于近年低复杂度路线映射，不作为默认正式实验主对照

### 本文新增工程设计

- 增量 Gram 缓存与稳定 fallback 求解流程
- 统一的实验输出组织：`results/raw`、`results/aggregated`、`results/logs`
- 消融实验与参数敏感性实验脚本
- 图表索引、来源映射、算法边界和交付检查文档

## 环境与安装

标准文档推荐主栈为：

- Python 3.10 / 3.11
- `numpy`
- `scipy`
- `pandas`
- `matplotlib`
- `tqdm`
- `scikit-learn`（仅用于 OMP 结果校验或对照）

当前仓库实际创建并使用的本地虚拟环境为 Windows Python `3.14.3`，对应 [`.venv/pyvenv.cfg`](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/.venv/pyvenv.cfg)。因此：

- 若按当前项目环境复现，请直接使用现有 `.venv` 或同版本 Python
- 若按标准文档口径答辩，可说明“工程依赖保持轻量，推荐兼容 Python 3.10 / 3.11；当前本地验证环境为 Python 3.14.3”

安装依赖：

PowerShell：

```powershell
py -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

CMD：

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

如果在 WSL 中运行，请单独创建 Linux 虚拟环境，不要复用 Windows 的 `.venv`。当前仓库默认按 Windows 本地 Python `3.14.3` 虚拟环境组织和验证。

## 如何运行实验

### 运行单个实验

```bash
python main.py --exp sparsity
python main.py --exp snr
python main.py --exp runtime
python main.py --exp compression
python main.py --exp matrix_type
python main.py --exp coeff_mode
python main.py --exp ablation
python main.py --exp param_sensitivity
```

### 一键运行全部正式实验

```bash
python main.py --all
```

### 常用可选参数

```bash
python main.py --exp snr --seed 20260408 --trials 10 --outdir .
```

说明：

- `--seed`：覆盖默认随机种子
- `--trials`：覆盖配置中的试验次数
- `--outdir`：指定结果输出根目录，默认当前目录

## 实验内容

当前正式实验包括：

- `sparsity`：稀疏度扫描
- `snr`：信噪比扫描
- `runtime`：运行时间实验
- `compression`：压缩率 `m/n` 扫描
- `matrix_type`：测量矩阵类型对比
- `coeff_mode`：非零系数分布对比
- `ablation`：改进模块消融实验
- `param_sensitivity`：关键参数敏感性实验

核心评价指标包括：

- `exact_support_recovery`
- `support_recall`
- `support_precision`
- `nmse`
- `relative_l2_error`
- `runtime_sec`
- `iterations`
- `final_residual_norm`
- `stop_reason`

## 结果输出位置

- 原始 trial 结果：`results/raw/`
- 聚合统计结果：`results/aggregated/`
- 运行日志与配置快照：`results/logs/`
- 论文可用图表：`figures/`

## 关键文档位置

- 来源映射文档：`docs/source_traceability.md`
- 算法边界说明：`docs/algorithm_boundary.md`
- 实验协议：`docs/experiment_protocol.md`
- 图表索引：`docs/experiment_figure_index.md`
- 最终交付检查清单：`docs/final_delivery_checklist.md`
- GitHub 提交说明：`docs/github_submission.md`

其中：

- `docs/source_traceability.md` 用于区分核心直接映射、理论支撑、启发映射和有限联系
- `docs/algorithm_boundary.md` 用于明确哪些内容属于文献复现、文献启发下改造和本文新增工程设计

## 项目结构

```text
thesis_sparse_recovery/
├─ algorithms/
├─ utils/
├─ experiments/
├─ configs/
├─ results/
│  ├─ raw/
│  ├─ aggregated/
│  └─ logs/
├─ figures/
├─ docs/
├─ main.py
├─ requirements.txt
└─ README.md
```

## 当前已知限制

- `rmp.py` 为探索性实现，保留近年路线映射与接口位置，但不作为默认正式实验主对照
- 增量求解当前主路径为 Gram 缓存求解，尚未扩展到更复杂的增量 Cholesky / QR 分解
- 配置文件现已使用真实 YAML 语法，并由项目内置的轻量解析逻辑加载，保持零额外 YAML 依赖
- 工程重点是答辩级实验复现与来源追踪，不扩展到预处理 gOMP、多路径追踪或块稀疏主线

## GitHub 仓库提交建议

本项目已经适合直接作为 GitHub 仓库提交，建议保留：

- 源代码、配置、文档和测试
- `results/raw/`、`results/aggregated/`、`figures/` 中的最终交付产物

默认忽略：

- `.venv/`
- `__pycache__/`
- `.idea/`
- `results/logs/` 中的时间戳日志

具体提交流程见 [`docs/github_submission.md`](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/docs/github_submission.md)。
