#!/usr/bin/env python3
"""Generate text summaries from the current experiment code outputs.

The generated files are intentionally data-driven. Do not hard-code old
experiment conclusions here; if the CSV changes, rerun this script.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw"
AGG = ROOT / "results" / "aggregated"
FIG = ROOT / "figures"
BASE = ROOT / "deepseek_ready"
OUT_CSV = BASE / "csv_text_summaries"
OUT_FIG = BASE / "figure_text_summaries"

KEY_METRICS = [
    "exact_support_recovery",
    "support_recall",
    "support_precision",
    "nmse",
    "relative_l2_error",
    "runtime_sec",
    "iterations",
    "final_residual_norm",
]


@dataclass(frozen=True)
class ExperimentSpec:
    name: str
    axis: str | None
    purpose: str
    note: str


EXPERIMENTS = [
    ExperimentSpec(
        "sparsity",
        "k",
        "比较不同稀疏度 k 下 OMP、gOMP、Improved-gOMP 的恢复性能和运行时间。",
        "当前 CSV 同时包含 baseline 与 optimized；论文图默认使用 optimized。",
    ),
    ExperimentSpec(
        "snr",
        "snr_db",
        "比较不同信噪比下各算法的抗噪声恢复性能。",
        "当前配置包含 RMP，并同时导出 baseline 与 optimized。",
    ),
    ExperimentSpec(
        "runtime",
        "n",
        "比较不同信号维度 n 下 baseline 与 optimized 实现的运行时间。",
        "该实验是实现级 benchmark，写论文时应区分算法性能和工程实现加速。",
    ),
    ExperimentSpec(
        "compression",
        "measurement_ratio",
        "比较不同测量比率 m/n 下各算法的恢复性能。",
        "m 由 measurement_ratio 和 n 动态计算，min_m=48。",
    ),
    ExperimentSpec(
        "matrix_type",
        "matrix_kind",
        "比较不同测量矩阵类型对恢复性能的影响。",
        "当前实验不包含 RMP。",
    ),
    ExperimentSpec(
        "coeff_mode",
        "coeff_mode",
        "比较不同稀疏系数分布对恢复性能的影响。",
        "当前实验不包含 RMP。",
    ),
    ExperimentSpec(
        "ablation",
        "ablation_variant",
        "比较 Improved-gOMP 相关模块组合的消融表现。",
        "消融实验只包含 optimized 实现，algorithm 列是模块组合名称。",
    ),
    ExperimentSpec(
        "param_sensitivity",
        None,
        "分析 Improved-gOMP 的 screening_ratio 和 group_size 参数敏感性。",
        "screening_ratio 与 group_size 分两组扫描，因此另一参数列存在结构性空值。",
    ),
    ExperimentSpec(
        "ablation_clean",
        "ablation_variant",
        "无噪声条件下的消融实验补充数据。",
        "该文件是补充实验输出，不是 main.py 的默认 ablation 文件。",
    ),
    ExperimentSpec(
        "ablation_noise_snr15",
        "ablation_variant",
        "SNR=15dB 噪声条件下的消融实验补充数据。",
        "该文件是补充实验输出，不是 main.py 的默认 ablation 文件。",
    ),
    ExperimentSpec(
        "sparsity_clean",
        "k",
        "无噪声条件下的稀疏度补充实验。",
        "该文件是补充实验输出，需结合文件内 m/n/SNR 字段确认条件。",
    ),
    ExperimentSpec(
        "sparsity_clean_easy",
        "k",
        "较容易无噪声条件下的稀疏度补充实验。",
        "该文件是补充实验输出，需结合文件内 m/n/SNR 字段确认条件。",
    ),
    ExperimentSpec(
        "sparsity_clean_hard",
        "k",
        "较困难无噪声条件下的稀疏度补充实验。",
        "该文件是补充实验输出，需结合文件内 m/n/SNR 字段确认条件。",
    ),
    ExperimentSpec(
        "sparsity_clean_m96",
        "k",
        "m=96 无噪声条件下的稀疏度补充实验。",
        "该文件是补充实验输出，需结合正式图表选择使用。",
    ),
]


FIGURE_SOURCES = {
    "sparsity": "sparsity",
    "sparsity_easy": "sparsity_clean_easy",
    "sparsity_m96": "sparsity_clean_m96",
    "snr": "snr",
    "runtime": "runtime",
    "compression": "compression",
    "matrix_type": "matrix_type",
    "coeff_mode": "coeff_mode",
    "ablation_clean": "ablation_clean",
    "ablation_noise": "ablation_noise_snr15",
    "ablation": "ablation",
    "param": "param_sensitivity",
}


OFFICIAL_FIGURES = [
    "sparsity_exact_support.png",
    "sparsity_nmse.png",
    "sparsity_runtime.png",
    "snr_nmse.png",
    "snr_support_recall.png",
    "snr_runtime.png",
    "runtime_compare.png",
    "compression_exact_support.png",
    "compression_nmse.png",
    "compression_runtime.png",
    "matrix_type_exact_support.png",
    "matrix_type_nmse.png",
    "coeff_mode_exact_support.png",
    "coeff_mode_nmse.png",
    "coeff_mode_runtime.png",
    "ablation_exact_support.png",
    "ablation_nmse.png",
    "ablation_runtime.png",
    "param_screening_ratio.png",
    "param_group_size.png",
]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(RAW / f"{name}.csv")


def sorted_values(values: Iterable[object]) -> list[object]:
    cleaned = [v for v in values if not pd.isna(v)]
    numeric: list[float] = []
    non_numeric: list[object] = []
    for value in cleaned:
        try:
            numeric.append(float(value))
        except (TypeError, ValueError):
            non_numeric.append(value)
    numeric_sorted: list[object] = []
    for value in sorted(numeric):
        if float(value).is_integer():
            numeric_sorted.append(int(value))
        else:
            numeric_sorted.append(value)
    return [*numeric_sorted, *sorted(non_numeric, key=str)]


def fmt(value: object) -> str:
    if pd.isna(value):
        return "NA"
    if isinstance(value, (float, np.floating)):
        if abs(float(value)) < 1e-4 and float(value) != 0.0:
            return f"{float(value):.3e}"
        return f"{float(value):.6f}".rstrip("0").rstrip(".")
    return str(value)


def impl_for_paper(df: pd.DataFrame) -> pd.DataFrame:
    if "implementation" in df.columns and "optimized" in set(df["implementation"].dropna()):
        return df[df["implementation"] == "optimized"].copy()
    return df.copy()


def group_columns(df: pd.DataFrame, axis: str | None) -> list[str]:
    cols: list[str] = []
    if axis and axis in df.columns:
        cols.append(axis)
    if "algorithm" in df.columns:
        cols.append("algorithm")
    if "implementation" in df.columns:
        cols.append("implementation")
    return cols


def metric_range_lines(df: pd.DataFrame) -> list[str]:
    lines = []
    for metric in KEY_METRICS:
        if metric not in df.columns:
            continue
        series = pd.to_numeric(df[metric], errors="coerce").dropna()
        if series.empty:
            continue
        lines.append(
            f"- {metric}: min={fmt(series.min())}, max={fmt(series.max())}, mean={fmt(series.mean())}"
        )
    return lines


def grouped_metric_table(df: pd.DataFrame, axis: str | None, max_rows: int = 80) -> list[str]:
    cols = group_columns(df, axis)
    metrics = [m for m in KEY_METRICS[:6] if m in df.columns]
    if not cols or not metrics:
        return ["无可分组指标表。"]
    grouped = df.groupby(cols, dropna=False)[metrics].mean(numeric_only=True).reset_index()
    grouped = grouped.sort_values(cols, key=lambda col: col.map(str))
    if len(grouped) > max_rows:
        grouped = grouped.head(max_rows)
        truncated = True
    else:
        truncated = False
    lines = []
    header = " | ".join([*cols, *metrics])
    lines.append(header)
    lines.append(" | ".join(["---"] * (len(cols) + len(metrics))))
    for _, row in grouped.iterrows():
        lines.append(" | ".join(fmt(row[c]) for c in [*cols, *metrics]))
    if truncated:
        lines.append(f"表格超过 {max_rows} 行，已截断；完整数据见对应 CSV。")
    return lines


def param_sensitivity_tables(df: pd.DataFrame) -> list[str]:
    lines: list[str] = []
    metrics = [
        "screening_pool_size_avg",
        "exact_support_recovery",
        "support_recall",
        "support_precision",
        "nmse",
        "runtime_sec",
        "iterations",
    ]
    for axis in ["screening_ratio", "group_size"]:
        if axis not in df.columns:
            continue
        part = df[df[axis].notna()].copy()
        if part.empty:
            continue
        available_metrics = [metric for metric in metrics if metric in part.columns]
        grouped = part.groupby(axis, dropna=False)[available_metrics].mean(numeric_only=True).reset_index()
        grouped = grouped.sort_values(axis)
        lines.extend(["", f"{axis} 分组均值："])
        lines.append(" | ".join([axis, *available_metrics]))
        lines.append(" | ".join(["---"] * (1 + len(available_metrics))))
        for _, row in grouped.iterrows():
            lines.append(" | ".join(fmt(row[col]) for col in [axis, *available_metrics]))
    return lines


def conclusion_lines(df: pd.DataFrame, axis: str | None) -> list[str]:
    paper_df = impl_for_paper(df)
    lines = [
        "可以写入论文的真实结论：",
        "- 当前结论仅对应本 CSV 中的参数设置，不能外推到所有压缩感知场景。",
    ]
    if axis and axis in paper_df.columns:
        lines.append(f"- 实验变量为 {axis}，取值为 {', '.join(map(fmt, sorted_values(paper_df[axis].unique())))}。")
    if "algorithm" in paper_df.columns and "exact_support_recovery" in paper_df.columns:
        by_algo = paper_df.groupby("algorithm")["exact_support_recovery"].mean().sort_values(ascending=False)
        if not by_algo.empty:
            best = by_algo.index[0]
            lines.append(
                f"- 按 optimized 数据的平均 exact_support_recovery 计算，最高算法/配置为 {best}，均值为 {fmt(by_algo.iloc[0])}。"
            )
    if "runtime_sec" in paper_df.columns and "algorithm" in paper_df.columns:
        by_time = paper_df.groupby("algorithm")["runtime_sec"].mean().sort_values()
        if not by_time.empty:
            fastest = by_time.index[0]
            lines.append(f"- 平均运行时间最短的是 {fastest}，均值为 {fmt(by_time.iloc[0])} 秒。")
    if "implementation" in df.columns and set(df["implementation"].dropna()) >= {"baseline", "optimized"}:
        lines.append("- CSV 同时包含 baseline 与 optimized；涉及加速比时必须明确比较的是实现优化，不是算法理论优势。")
    lines.extend(
        [
            "",
            "不能写入论文的错误结论：",
            "- 不得声称 Improved-gOMP 在所有实验条件下都显著优于 OMP/gOMP，除非对应 CSV 的分组数据支持。",
            "- 不得把 exact_support_recovery 较低的结果写成稳定精确恢复。",
            "- 不得引用本文件不存在的参数点、SNR 点、测量比率或算法。",
            "- 不得把 baseline 与 optimized 混在一起计算同一条论文曲线。",
        ]
    )
    return lines


def summarize_csv(spec: ExperimentSpec) -> None:
    csv_path = RAW / f"{spec.name}.csv"
    if not csv_path.exists():
        return
    df = read_csv(spec.name)
    paper_df = impl_for_paper(df)

    lines = [
        f"文件：results/raw/{spec.name}.csv",
        f"生成依据：当前 results/raw CSV；不是旧 README 或旧审计文档。",
        "",
        "实验目的：",
        spec.purpose,
        "",
        "使用说明：",
        spec.note,
        "",
        "基本事实：",
        f"- 行数：{len(df)}",
        f"- 列数：{len(df.columns)}",
    ]
    if spec.axis and spec.axis in df.columns:
        lines.append(f"- 实验变量 {spec.axis}：{', '.join(map(fmt, sorted_values(df[spec.axis].unique())))}")
    if "algorithm" in df.columns:
        lines.append(f"- 算法/配置：{', '.join(map(str, sorted_values(df['algorithm'].unique())))}")
    if "implementation" in df.columns:
        lines.append(f"- implementation：{', '.join(map(str, sorted_values(df['implementation'].unique())))}")
    for col in ["m", "n", "k", "measurement_ratio", "matrix_kind", "coeff_mode", "snr_db"]:
        if col in df.columns:
            vals = sorted_values(df[col].unique())
            if len(vals) <= 12:
                lines.append(f"- {col}：{', '.join(map(fmt, vals))}")

    lines.extend(["", "核心指标范围：", *metric_range_lines(df), "", "论文默认 optimized 分组均值："])
    lines.extend(grouped_metric_table(paper_df, spec.axis))
    if spec.name == "param_sensitivity":
        lines.extend(param_sensitivity_tables(paper_df))
    lines.extend(["", *conclusion_lines(df, spec.axis)])
    write(OUT_CSV / f"{spec.name}.txt", "\n".join(lines))


def infer_figure_source(fig_name: str) -> str | None:
    stem = fig_name.removesuffix(".png")
    for prefix in sorted(FIGURE_SOURCES, key=len, reverse=True):
        if stem.startswith(prefix):
            return FIGURE_SOURCES[prefix]
    return None


def figure_metric(fig_name: str) -> tuple[str, str]:
    stem = fig_name.removesuffix(".png")
    if "exact_support" in stem:
        return "exact_support_recovery", "严格支持集完全恢复率"
    if "support_recall" in stem:
        return "support_recall", "支持集召回率"
    if "runtime" in stem or "compare" in stem:
        return "runtime_sec", "运行时间"
    if "nmse" in stem:
        return "nmse", "归一化均方误差"
    if "screening_ratio" in stem:
        return "nmse", "NMSE"
    if "group_size" in stem:
        return "nmse", "NMSE"
    return "unknown", "见图中纵轴"


def summarize_figure(fig_path: Path) -> None:
    source = infer_figure_source(fig_path.name)
    metric, ylabel = figure_metric(fig_path.name)
    official = fig_path.name in OFFICIAL_FIGURES
    source_path = RAW / f"{source}.csv" if source else None

    lines = [
        f"图片：figures/{fig_path.name}",
        f"文件大小：{fig_path.stat().st_size} bytes",
        f"推荐状态：{'主文正式候选图' if official else '补充/附录候选图，正文空间不足时放入附录或补充分析'}",
        "",
    ]
    if source and source_path and source_path.exists():
        df = read_csv(source)
        axis = next((spec.axis for spec in EXPERIMENTS if spec.name == source), None)
        lines.extend(
            [
                f"来源数据：results/raw/{source}.csv",
                f"横轴：{axis if axis else '参数扫描变量'}",
                f"纵轴：{ylabel}（{metric}）",
                f"算法/曲线：{', '.join(map(str, sorted_values(df['algorithm'].unique()))) if 'algorithm' in df.columns else '见 CSV'}",
            ]
        )
        if "implementation" in df.columns:
            lines.append("implementation：图通常应使用 optimized；如图含 baseline/optimized，正文必须明确说明。")
        if metric in df.columns:
            paper_df = impl_for_paper(df)
            lines.append("关键数据范围：")
            for algo, group in paper_df.groupby("algorithm") if "algorithm" in paper_df.columns else []:
                lines.append(
                    f"- {algo}: {metric} mean={fmt(group[metric].mean())}, min={fmt(group[metric].min())}, max={fmt(group[metric].max())}"
                )
    else:
        lines.extend(["来源数据：未能根据文件名前缀自动确认。", "使用前必须人工确认该图由哪个 CSV 生成。"])

    lines.extend(
        [
            "",
            "建议正文使用：",
            "- 只描述图中由 CSV 支持的趋势，避免使用“显著优于”“稳定恢复”等过强表述。",
            "- 图题应包含关键实验条件，例如 m、n、k、SNR、implementation。",
            "",
            "禁止正文：",
            "- 不得把补充/附录候选图混入主文编号，除非 insertion_plan 明确调整。",
            "- 不得引用图片中不存在的数据点或旧文档中的旧参数。",
        ]
    )
    write(OUT_FIG / f"{fig_path.stem}.txt", "\n".join(lines))


def generate_verified_data() -> None:
    lines = [
        "# Verified Current Data - 当前实验数据审计",
        "",
        "生成依据：当前 `experiments/*.py`、`configs/*.yaml` 和 `results/raw/*.csv`。",
        "本文件用于替代旧审计口径；若重新运行实验，需重新生成。",
        "",
        "## 实验文件完整性",
        "",
        "| 实验 | raw CSV 行数 | aggregated 是否存在 | 变量 | 算法/配置 | implementation |",
        "|---|---:|---|---|---|---|",
    ]
    for spec in EXPERIMENTS:
        csv_path = RAW / f"{spec.name}.csv"
        if not csv_path.exists():
            continue
        df = read_csv(spec.name)
        agg_path = AGG / f"summary_{spec.name}.csv"
        axis_vals = ""
        if spec.axis and spec.axis in df.columns:
            vals = sorted_values(df[spec.axis].unique())
            axis_vals = f"{spec.axis}={', '.join(map(fmt, vals))}"
        algos = ", ".join(map(str, sorted_values(df["algorithm"].unique()))) if "algorithm" in df.columns else ""
        impls = ", ".join(map(str, sorted_values(df["implementation"].unique()))) if "implementation" in df.columns else ""
        lines.append(f"| {spec.name} | {len(df)} | {'是' if agg_path.exists() else '否'} | {axis_vals} | {algos} | {impls} |")

    lines.extend(
        [
            "",
            "## 关键注意事项",
            "",
            "- 当前普通 sweep 多数包含 `baseline` 与 `optimized` 两套 implementation；论文图和结论必须说明采用哪一套。",
            "- 当前 `snr.csv` 包含 8 个 SNR 点：5, 10, 15, 20, 25, 30, 40, clean。",
            "- 当前 `compression.csv` 包含 8 个 measurement_ratio 点：0.1875 到 0.625。",
            "- 当前 `runtime.csv` 为每个 n/algorithm/implementation 20 次试验。",
            "- `param_sensitivity.csv` 中 `screening_ratio` 与 `group_size` 是分开扫描，另一列为空是结构性空值。",
            "- `fallback_reason` 为空通常表示没有 fallback，不是实验失败。",
            "",
            "## 论文写作约束",
            "",
            "- 每个数字必须追溯到 `results/raw/*.csv` 或 `results/aggregated/*.csv` 的具体列。",
            "- 旧 README、旧 docs、旧 `deepseek_ready` 说明若与当前 CSV 冲突，以当前代码和 CSV 为准。",
            "- backup/辅助图也可纳入附录或补充分析，但不得混入主文正式图编号。",
        ]
    )
    write(BASE / "verified_existing_data.md", "\n".join(lines))


def generate_insertion_plan() -> None:
    rows = [
        ("4.2 稀疏度实验", "图4.1", "figures/sparsity_exact_support.png", "results/raw/sparsity.csv", "不同 k 下 ESR 对比"),
        ("4.2 稀疏度实验", "图4.2", "figures/sparsity_nmse.png", "results/raw/sparsity.csv", "不同 k 下 NMSE 对比"),
        ("4.2 稀疏度实验", "图4.3", "figures/sparsity_runtime.png", "results/raw/sparsity.csv", "不同 k 下运行时间对比"),
        ("4.3 信噪比实验", "图4.4", "figures/snr_nmse.png", "results/raw/snr.csv", "不同 SNR 下 NMSE 对比"),
        ("4.3 信噪比实验", "图4.5", "figures/snr_support_recall.png", "results/raw/snr.csv", "不同 SNR 下支持召回率对比"),
        ("4.3 信噪比实验", "图4.6", "figures/snr_runtime.png", "results/raw/snr.csv", "不同 SNR 下运行时间对比"),
        ("4.4 运行时间实验", "图4.7", "figures/runtime_compare.png", "results/raw/runtime.csv", "baseline 与 optimized 运行时间对比"),
        ("4.5 压缩比实验", "图4.8", "figures/compression_exact_support.png", "results/raw/compression.csv", "不同测量比率下 ESR 对比"),
        ("4.5 压缩比实验", "图4.9", "figures/compression_nmse.png", "results/raw/compression.csv", "不同测量比率下 NMSE 对比"),
        ("4.5 压缩比实验", "图4.10", "figures/compression_runtime.png", "results/raw/compression.csv", "不同测量比率下运行时间对比"),
        ("4.6 矩阵类型实验", "图4.11", "figures/matrix_type_exact_support.png", "results/raw/matrix_type.csv", "不同矩阵类型下 ESR 对比"),
        ("4.6 矩阵类型实验", "图4.12", "figures/matrix_type_nmse.png", "results/raw/matrix_type.csv", "不同矩阵类型下 NMSE 对比"),
        ("4.7 系数分布实验", "图4.13", "figures/coeff_mode_exact_support.png", "results/raw/coeff_mode.csv", "不同系数分布下 ESR 对比"),
        ("4.7 系数分布实验", "图4.14", "figures/coeff_mode_nmse.png", "results/raw/coeff_mode.csv", "不同系数分布下 NMSE 对比"),
        ("4.7 系数分布实验", "图4.15", "figures/coeff_mode_runtime.png", "results/raw/coeff_mode.csv", "不同系数分布下运行时间对比"),
        ("4.8 消融实验", "图4.16", "figures/ablation_exact_support.png", "results/raw/ablation.csv", "模块组合 ESR 对比"),
        ("4.8 消融实验", "图4.17", "figures/ablation_nmse.png", "results/raw/ablation.csv", "模块组合 NMSE 对比"),
        ("4.8 消融实验", "图4.18", "figures/ablation_runtime.png", "results/raw/ablation.csv", "模块组合运行时间对比"),
        ("4.9 参数敏感性", "图4.19", "figures/param_screening_ratio.png", "results/raw/param_sensitivity.csv", "screening_ratio 敏感性"),
        ("4.9 参数敏感性", "图4.20", "figures/param_group_size.png", "results/raw/param_sensitivity.csv", "group_size 敏感性"),
    ]
    lines = [
        "# Insertion Plan - 当前代码口径图表插入计划",
        "",
        "生成依据：当前 `results/raw/*.csv` 与 `figures/*.png`。实验范围已锁定为：主实验、补充 clean/noise 实验、参数敏感性实验均尽可能纳入论文；主文空间不足时进入附录或补充分析。",
        "",
        "## 主文正式候选图",
        "",
        "| 章节 | 编号 | 图片 | 数据来源 | 用途 |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    aux = sorted(p.name for p in FIG.glob("*.png") if p.name not in OFFICIAL_FIGURES)
    lines.extend(
        [
            "",
            "## 补充或附录候选图",
            "",
            "以下图片存在于 `figures/`，建议尽可能纳入论文的补充分析或附录；如需放入正文，必须先调整主文图号和正文叙述：",
            "",
            *[f"- figures/{name}" for name in aux],
            "",
            "## 表格建议",
            "",
            "- 表4.1：实验默认参数设置，来源 `configs/*.yaml` 和对应实验入口。",
            "- 表4.2：baseline vs optimized 加速比汇总，来源 `results/aggregated/summary_speedup_*.csv` 或 `results/raw/runtime.csv`。",
            "- 表4.3：消融实验配置说明，来源 `experiments/run_ablation.py`。",
            "- 表4.4：参数敏感性关键结果，来源 `results/raw/param_sensitivity.csv`。",
            "",
            "## 全局限制",
            "",
            "- 正文中每个数值必须标明可追溯 CSV、列名和筛选条件。",
            "- 图题必须包含关键实验条件，至少包括 m、n、k、SNR 或扫描变量，以及 implementation 口径。",
            "- 如图采用 optimized 数据，正文不能把它描述为 baseline 结果。",
            "- 补充或附录图也必须有正文/附录引用、图题和数据来源。",
            "- 旧文档中与当前 CSV 不一致的 SNR 点、测量比率、trial 数均不得继续使用。",
        ]
    )
    write(BASE / "insertion_plan.md", "\n".join(lines))


def generate_all() -> None:
    OUT_CSV.mkdir(parents=True, exist_ok=True)
    OUT_FIG.mkdir(parents=True, exist_ok=True)
    for spec in EXPERIMENTS:
        summarize_csv(spec)
    for fig_path in sorted(FIG.glob("*.png")):
        summarize_figure(fig_path)
    generate_verified_data()
    generate_insertion_plan()

    print("Generated current summaries.")
    print(f"CSV summaries: {len(list(OUT_CSV.glob('*.txt')))}")
    print(f"Figure summaries: {len(list(OUT_FIG.glob('*.txt')))}")
    print("verified_existing_data.md: OK")
    print("insertion_plan.md: OK")


if __name__ == "__main__":
    generate_all()
