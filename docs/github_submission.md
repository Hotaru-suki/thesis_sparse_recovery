# GitHub 提交说明

本项目当前已经整理为适合直接提交到 GitHub 的论文实验工程仓库。

## 建议提交内容

- 代码目录：`algorithms/`、`utils/`、`experiments/`、`tests/`
- 配置目录：`configs/`
- 文档目录：`docs/`
- 主入口与依赖：`main.py`、`requirements.txt`、`README.md`
- 可复现实验产物：
  - `results/raw/`
  - `results/aggregated/`
  - `figures/`

## 默认不建议提交的内容

- `.venv/`
- `__pycache__/`
- `.idea/`
- `results/logs/` 下按时间戳生成的运行日志

这些内容已经写入 [`.gitignore`](/mnt/c/Users/siest/Desktop/thesis_sparse_recovery/.gitignore)。

## 建议的仓库结构说明

提交到 GitHub 时，推荐在仓库首页说明以下几点：

- 这是毕业设计配套实验工程，不是通用算法库
- 默认主线算法为 `OMP`、`gOMP`、`Improved-gOMP`
- `RMP` 为受控近年对照实现
- `results/` 与 `figures/` 中的文件用于论文复现与答辩展示

## 建议提交流程

```bash
git init
git add .
git status
git commit -m "Initial thesis sparse recovery experiment project"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

## 提交前自检

- `README.md` 是否与当前代码入口一致
- `configs/` 是否全部可加载
- `tests/` 是否能运行
- `results/raw/`、`results/aggregated/`、`figures/` 是否为你希望展示的最终版本
- 是否包含不应公开的个人路径、缓存文件或本地环境文件
