from __future__ import annotations

import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _parse_scalar(text: str) -> Any:
    value = text.strip()
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item) for item in inner.split(",")]
    if value.startswith('"') or value.startswith("'"):
        return ast.literal_eval(value)
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def _load_simple_yaml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line:
            continue
        if ":" not in line:
            raise ValueError(f"Unsupported YAML line: {raw_line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Invalid YAML key in line: {raw_line}")
        data[key] = _parse_scalar(value) if value else None
    return data


def load_config(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        return json.loads(text)
    if suffix in {".yaml", ".yml"}:
        return _load_simple_yaml(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return _load_simple_yaml(text)


def timestamp_string() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_output_dirs(outdir: str | Path) -> dict[str, Path]:
    root = Path(outdir)
    paths = {
        "root": root,
        "raw": root / "results" / "raw",
        "aggregated": root / "results" / "aggregated",
        "logs": root / "results" / "logs",
        "figures": root / "figures",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def save_results(raw_df: Any, summary_df: Any, raw_path: str | Path, summary_path: str | Path) -> None:
    raw_path = Path(raw_path)
    summary_path = Path(summary_path)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    raw_df.to_csv(raw_path, index=False)
    summary_df.to_csv(summary_path, index=False)


def save_run_metadata(log_dir: str | Path, experiment_name: str, config: dict[str, Any], success: bool = True) -> Path:
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": timestamp_string(),
        "experiment": experiment_name,
        "config": config,
        "success": success,
    }
    out_path = log_dir / f"{experiment_name}_{payload['timestamp']}.json"
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    return out_path
