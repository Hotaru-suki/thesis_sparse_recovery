from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "configs"


def get_config_path(name: str) -> Path:
    return CONFIG_DIR / f"{name}.yaml"
