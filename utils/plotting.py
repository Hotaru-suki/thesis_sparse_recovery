from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib.pyplot as plt


_PAPER_FIGSIZE = (10.5, 5.8)
_ROTATED_LABEL_MAX_LEN = 10


def _sorted_group(group: pd.DataFrame, x_col: str) -> pd.DataFrame:
    numeric = pd.to_numeric(group[x_col], errors="coerce")
    if numeric.notna().all():
        return group.assign(_sort_key=numeric).sort_values("_sort_key").drop(columns="_sort_key")
    if numeric.notna().any():
        fallback = numeric.fillna(numeric.max() + 1.0)
        return group.assign(_sort_key=fallback).sort_values("_sort_key").drop(columns="_sort_key")
    return group


def _format_tick_label(label: object) -> str:
    text = str(label)
    replacements = {
        "gOMP+AdaptiveScreen": "gOMP+\nAdaptive\nScreen",
        "gOMP+IncrementalSolver": "gOMP+\nIncremental\nSolver",
        "gOMP+NoiseAwareStop": "gOMP+\nNoiseAware\nStop",
        "gOMP+Adaptive+Incremental": "gOMP+\nAdaptive+\nIncremental",
        "gOMP+Adaptive+NoiseAware": "gOMP+\nAdaptive+\nNoiseAware",
        "gOMP+Incremental+NoiseAware": "gOMP+\nIncremental+\nNoiseAware",
        "Improved-gOMP": "Improved-\ngOMP",
        "partial_dct": "partial\nDCT",
        "rademacher": "Rademacher",
        "gaussian": "Gaussian",
        "uniform": "Uniform",
        "decay": "Decay",
    }
    return replacements.get(text, text.replace("_", "\n") if len(text) > _ROTATED_LABEL_MAX_LEN else text)


def _needs_rotated_labels(labels: list[object]) -> bool:
    return any(len(str(label)) > _ROTATED_LABEL_MAX_LEN for label in labels)


def plot_metric(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    out_path: str | Path,
    title: str,
    xlabel: str,
    ylabel: str,
) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=_PAPER_FIGSIZE)
    x_numeric = pd.to_numeric(df[x_col], errors="coerce")
    mixed_axis = x_numeric.isna().any()
    x_mapping: dict[object, int] = {}
    if mixed_axis:
        axis_frame = pd.DataFrame({x_col: df[x_col]})
        axis_frame["_sort_key"] = pd.to_numeric(axis_frame[x_col], errors="coerce")
        axis_frame["_sort_key"] = axis_frame["_sort_key"].fillna(axis_frame["_sort_key"].max() + 1.0)
        ordered_labels = axis_frame.sort_values("_sort_key")[x_col].drop_duplicates().tolist()
        x_mapping = {label: idx for idx, label in enumerate(ordered_labels)}

    for algo, group in df.groupby("algorithm"):
        ordered = _sorted_group(group, x_col)
        x_values = [x_mapping[value] for value in ordered[x_col]] if mixed_axis else ordered[x_col]
        ax.plot(x_values, ordered[y_col], marker="o", linewidth=2, label=algo)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if mixed_axis:
        labels = list(x_mapping.keys())
        rotation = 30 if _needs_rotated_labels(labels) else 0
        ax.set_xticks(
            list(x_mapping.values()),
            [_format_tick_label(label) for label in labels],
            rotation=rotation,
            ha="right" if rotation else "center",
        )
    else:
        labels = df[x_col].drop_duplicates().tolist()
        if _needs_rotated_labels(labels):
            ax.tick_params(axis="x", labelrotation=30)
            for tick in ax.get_xticklabels():
                tick.set_ha("right")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout(pad=1.1)
    fig.subplots_adjust(bottom=0.24 if mixed_axis and _needs_rotated_labels(list(x_mapping.keys())) else 0.15)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
