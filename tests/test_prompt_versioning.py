import os
import sys
import tempfile
import unittest

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient


class PromptVersioningTests(unittest.TestCase):
    def setUp(self):
        os.environ["LUTHOR_ENCODER_LATENT_DIM"] = "4"
        os.environ["LUTHOR_ENCODER_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_ENCODER_NUM_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_PREDICTOR_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_USE_ATTENTION"] = "true"
        os.environ["LUTHOR_PLANNER_LR"] = "0.01"
        os.environ["LUTHOR_AB_TESTING_ENABLED"] = "false"
        os.environ["LUTHOR_PROMPT_VERSION"] = "v2"

        from luthor.config import get_config, reset_config

        reset_config()
        self.config = get_config()

        from luthor.api.main import create_app

        self.app = create_app()
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.client.app.state.log_store = _MockLogStore()
        self.client.app.state.embedding_store = _MockEmbeddingStore()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        os.environ.pop("LUTHOR_PROMPT_VERSION", None)
        os.environ.pop("LUTHOR_AB_TESTING_ENABLED", None)
        from luthor.config import reset_config

        reset_config()

    def test_prompts_endpoint_lists_files(self):
        response = self.client.get("/prompts")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        names = {item["name"] for item in payload["prompts"]}
        self.assertIn("system_v1.txt", names)
        self.assertIn("system_v2.txt", names)
        self.assertTrue(all(item["content"] for item in payload["prompts"]))

    def test_params_prompt_version_is_read(self):
        self.assertEqual(self.config.prompt_version, "v2")

    def test_params_yaml_contains_prompt_version(self):
        params_path = os.path.join(os.path.dirname(__file__), "..", "params.yaml")
        with open(params_path, encoding="utf-8") as handle:
            params = yaml.safe_load(handle)
        self.assertEqual(params["prompt_version"], "v1")

    def test_human_oracle_logs_prompt(self):
        import logging
        from io import StringIO

        import torch

        from luthor.active_learning.human_oracle import HumanLabelOracle
        from luthor.environment.gridworld import GridWorld
        from luthor.prompts.loader import load_system_prompt

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        logger = logging.getLogger("luthor.active_learning.human_oracle")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        env = GridWorld(2, 2, noise_std=0.0, grid_size=6, obstacles=[(3, 3)], goal=[5.0, 5.0])
        oracle = HumanLabelOracle(env=env, prompt_version="v1")
        oracle.query(torch.tensor([1.0, 1.0]), torch.tensor([0.1, 0.2]))

        output = stream.getvalue()
        self.assertIn("prompt_version=v1", output)
        self.assertIn(load_system_prompt("v1").splitlines()[0], output)

        logger.removeHandler(handler)


class _MockLogStore:
    def ping(self) -> bool:
        return True

    def ensure_schema(self) -> None:
        return None

    def log_inference(self, **kwargs) -> int:
        return 1

    def log_active_learning_round(self, **kwargs) -> int:
        return 1

    def fetch_ab_metrics(self, **kwargs):
        return []


class _MockEmbeddingStore:
    def ping(self) -> bool:
        return True

    def add_embedding(self, embedding_id, embedding, metadata=None) -> None:
        return None


if __name__ == "__main__":
    unittest.main()
