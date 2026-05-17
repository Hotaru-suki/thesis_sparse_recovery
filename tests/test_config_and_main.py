from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

import main
from experiments.common import build_improved_gomp_kwargs
from experiments.run_param_sensitivity import _sensitivity_params
from utils.io_utils import load_config


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("123", 123),
        ("true", True),
        ("[gaussian, bernoulli]", ["gaussian", "bernoulli"]),
        ("0.375", 0.375),
        ("clean", "clean"),
    ],
)
def test_load_simple_yaml_scalars(tmp_path: Path, raw_value: str, expected: object) -> None:
    config_path = tmp_path / "sample.yaml"
    config_path.write_text(f"value: {raw_value}\n", encoding="utf-8")

    config = load_config(config_path)

    assert config["value"] == expected


def test_run_module_builds_expected_command() -> None:
    with mock.patch("subprocess.run") as mock_run:
        main.run_module("experiments.run_snr", seed=7, trials=3, outdir="tmp")

    mock_run.assert_called_once()
    cmd = mock_run.call_args.args[0]
    assert cmd[1:3] == ["-m", "experiments.run_snr"]
    assert "--seed" in cmd
    assert "--trials" in cmd
    assert "--outdir" in cmd


@pytest.mark.parametrize(
    ("argv", "expected_call"),
    [
        (["main.py", "--exp", "compression", "--seed", "42"], ("experiments.run_compression", 42, None, ".")),
        (
            ["main.py", "--exp", "snr", "--seed", "7", "--trials", "3", "--outdir", "tmp"],
            ("experiments.run_snr", 7, 3, "tmp"),
        ),
    ],
)
def test_main_dispatches_named_experiment(argv: list[str], expected_call: tuple[str, int | None, int | None, str]) -> None:
    with mock.patch("main.run_module") as mock_run, mock.patch("sys.argv", argv):
        main.main()

    mock_run.assert_called_once_with(*expected_call)


def test_main_dispatches_all_experiments() -> None:
    with mock.patch("main.run_module") as mock_run, mock.patch("sys.argv", ["main.py", "--all"]):
        main.main()

    assert mock_run.call_count == len(main.EXPERIMENT_MODULES)


@pytest.mark.parametrize(
    ("overrides", "expected_key", "expected_value"),
    [
        (
            {
                "screening_ratio": 5.0,
                "improved_screening_ratio": 5.0,
                "optimized_screening_ratio": 5.0,
            },
            "screening_ratio",
            5.0,
        ),
        ({"group_size": 5, "improved_group_size": 5}, "group_size", 5),
    ],
)
def test_param_sensitivity_overrides_reach_improved_gomp_kwargs(
    overrides: dict[str, object],
    expected_key: str,
    expected_value: object,
) -> None:
    config = {
        "improved_group_size": 2,
        "screening_ratio": 3.0,
        "use_incremental_solver": True,
    }
    params = _sensitivity_params(config, **overrides)
    kwargs = build_improved_gomp_kwargs(params, noise_sigma=None, implementation="optimized")

    assert kwargs[expected_key] == expected_value
    assert kwargs["profile_level"] == "full"
