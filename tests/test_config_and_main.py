from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import main
from utils.io_utils import load_config


class ConfigLoadingTests(unittest.TestCase):
    def test_load_simple_yaml_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "sample.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "seed: 123",
                        "outdir: .",
                        "use_noise_aware_stop: true",
                        "matrix_list: [gaussian, bernoulli]",
                    ]
                ),
                encoding="utf-8",
            )
            config = load_config(config_path)
        self.assertEqual(config["seed"], 123)
        self.assertEqual(config["outdir"], ".")
        self.assertTrue(config["use_noise_aware_stop"])
        self.assertEqual(config["matrix_list"], ["gaussian", "bernoulli"])


class MainDispatchTests(unittest.TestCase):
    def test_run_module_builds_expected_command(self) -> None:
        with mock.patch("subprocess.run") as mock_run:
            main.run_module("experiments.run_snr", seed=7, trials=3, outdir="tmp")
        mock_run.assert_called_once()
        cmd = mock_run.call_args.args[0]
        self.assertEqual(cmd[1:3], ["-m", "experiments.run_snr"])
        self.assertIn("--seed", cmd)
        self.assertIn("--trials", cmd)
        self.assertIn("--outdir", cmd)

    def test_main_dispatches_named_experiment(self) -> None:
        with mock.patch("main.run_module") as mock_run, mock.patch(
            "sys.argv", ["main.py", "--exp", "compression", "--seed", "42"]
        ):
            main.main()
        mock_run.assert_called_once_with("experiments.run_compression", 42, None, ".")

    def test_main_dispatches_all_experiments(self) -> None:
        with mock.patch("main.run_module") as mock_run, mock.patch("sys.argv", ["main.py", "--all"]):
            main.main()
        self.assertEqual(mock_run.call_count, len(main.EXPERIMENT_MODULES))


if __name__ == "__main__":
    unittest.main()
