import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.pipeline.prepare_data import prepare_data
from luthor.pipeline.train import run_training


MINIMAL_PARAMS = {
    "seed": 7,
    "gridworld": {
        "state_dim": 2,
        "action_dim": 2,
        "grid_size": 6,
        "noise_std": 0.0,
        "goal": [5.0, 5.0],
        "goal_tolerance": 0.5,
        "max_steps": 15,
        "obstacles": [[2, 2]],
    },
    "encoder": {
        "latent_dim": 4,
        "hidden_dim": 16,
        "num_layers": 2,
        "dropout": 0.1,
    },
    "predictor": {
        "hidden_dim": 16,
        "num_layers": 2,
        "dropout": 0.1,
        "use_attention": True,
    },
    "planner": {
        "horizon": 3,
        "num_samples": 5,
        "learning_rate": 0.01,
        "num_iterations": 2,
    },
    "active_learning": {
        "num_rounds": 2,
        "pool_size": 6,
        "query_batch_size": 2,
        "mc_samples": 2,
        "train_steps_per_round": 1,
        "input_dim": 2,
        "action_dim": 2,
        "human_in_loop": False,
    },
    "tools": {
        "weather": {
            "enabled": False,
            "api_url": "https://api.open-meteo.com/v1/forecast",
        },
    },
    "visualization": {
        "enabled": False,
        "output_dir": "./outputs",
        "save_plots": False,
        "show_plots": False,
    },
    "logging": {"level": "INFO"},
    "eval": {"episodes": 2, "train_steps_per_episode": 3},
    "memory": {
        "use_context_compression": False,
        "history_length": 5,
        "gru_hidden_dim": 16,
        "gru_num_layers": 1,
        "compress_source": "observation",
    },
}


class DvcPipelineTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.params_path = self.root / "params.yaml"
        with self.params_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(MINIMAL_PARAMS, handle)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_prepare_data_writes_versioned_gridworld(self):
        output = self.root / "data" / "raw" / "gridworld.json"
        prepare_data(self.params_path, output)

        with output.open(encoding="utf-8") as handle:
            spec = json.load(handle)

        self.assertEqual(spec["grid_size"], 6)
        self.assertEqual(spec["seed"], 7)
        self.assertIn("generated_at", spec)
        self.assertEqual(spec["obstacles"], [[2, 2]])

    def test_train_exports_metrics_json(self):
        gridworld_path = self.root / "data" / "raw" / "gridworld.json"
        metrics_path = self.root / "metrics.json"
        prepare_data(self.params_path, gridworld_path)

        metrics = run_training(self.params_path, gridworld_path, metrics_path)

        self.assertTrue(metrics_path.exists())
        self.assertIn("final_loss", metrics)
        self.assertIn("success_rate", metrics)
        self.assertIn("steps_per_episode", metrics)
        self.assertEqual(len(metrics["steps_per_episode"]), 2)

    def test_dvc_yaml_stages_match_pipeline_commands(self):
        dvc_path = Path(__file__).resolve().parents[1] / "dvc.yaml"
        with dvc_path.open(encoding="utf-8") as handle:
            pipeline = yaml.safe_load(handle)

        self.assertEqual(list(pipeline["stages"].keys()), ["prepare_data", "train"])

        prepare_cmd = pipeline["stages"]["prepare_data"]["cmd"]
        train_cmd = pipeline["stages"]["train"]["cmd"]
        self.assertIn("python3 -m luthor.pipeline.prepare_data", prepare_cmd)
        self.assertIn("python3 -m luthor.pipeline.train", train_cmd)
        self.assertIn("metrics.json", train_cmd)

    def test_dvc_repro_end_to_end(self):
        repo_root = Path(__file__).resolve().parents[1]
        workdir = self.root / "dvc-workspace"
        shutil.copytree(repo_root / "src", workdir / "src")
        shutil.copytree(repo_root / "data", workdir / "data")
        shutil.copy2(repo_root / "dvc.yaml", workdir / "dvc.yaml")
        shutil.copy2(repo_root / "params.yaml", workdir / "params.yaml")
        if (repo_root / ".dvc").exists():
            shutil.copytree(repo_root / ".dvc", workdir / ".dvc")

        fast_params = dict(MINIMAL_PARAMS)
        fast_params["planner"]["num_iterations"] = 1
        fast_params["active_learning"]["num_rounds"] = 1
        with (workdir / "params.yaml").open("w", encoding="utf-8") as handle:
            yaml.safe_dump(fast_params, handle)

        dvc_bin = shutil.which("dvc")
        if dvc_bin is None:
            dvc_bin = shutil.which("dvc", path=os.path.expanduser("~/.local/bin"))
        if dvc_bin is None:
            self.skipTest("dvc is not installed")

        env = os.environ.copy()
        env["PYTHONPATH"] = str(workdir / "src")

        git_init = subprocess.run(
            ["git", "init"],
            cwd=workdir,
            capture_output=True,
            text=True,
        )
        self.assertEqual(git_init.returncode, 0, git_init.stderr)

        if not (workdir / ".dvc").exists():
            init = subprocess.run(
                [dvc_bin, "init"],
                cwd=workdir,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(init.returncode, 0, init.stderr)

        repro = subprocess.run(
            [dvc_bin, "repro"],
            cwd=workdir,
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
        )
        self.assertEqual(repro.returncode, 0, repro.stdout + repro.stderr)

        metrics_path = workdir / "metrics.json"
        self.assertTrue(metrics_path.exists())
        with metrics_path.open(encoding="utf-8") as handle:
            metrics = json.load(handle)
        self.assertIn("final_loss", metrics)
        self.assertIn("success_rate", metrics)
        self.assertIn("steps_per_episode", metrics)


if __name__ == "__main__":
    unittest.main()
