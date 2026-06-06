import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import torch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class ABTestingTests(unittest.TestCase):
    def setUp(self):
        os.environ["LUTHOR_ENCODER_LATENT_DIM"] = "4"
        os.environ["LUTHOR_ENCODER_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_ENCODER_NUM_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_PREDICTOR_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_USE_ATTENTION"] = "true"
        os.environ["LUTHOR_PLANNER_LR"] = "0.01"
        os.environ["LUTHOR_AB_TESTING_ENABLED"] = "true"

        from luthor.config import get_config, reset_config

        reset_config()
        self.config = get_config()

        self.tempdir = tempfile.TemporaryDirectory()
        self.default_path = Path(self.tempdir.name) / "default.pth"
        self.candidate_path = Path(self.tempdir.name) / "candidate.pth"
        self._save_checkpoint(self.default_path, seed=1)
        self._save_checkpoint(self.candidate_path, seed=99)

        self.config.ab_testing.enabled = True
        self.config.ab_testing.models = {
            "default": str(self.default_path),
            "candidate": str(self.candidate_path),
        }

        from luthor.api.main import create_app

        self.mock_store = _MockLogStore()
        self.app = create_app()
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.client.app.state.config = self.config
        self.client.app.state.log_store = self.mock_store
        self.client.app.state.embedding_store = _MockEmbeddingStore()

        from luthor.api.services import JEPAService

        self.client.app.state.jepa_service = JEPAService(self.config)

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.tempdir.cleanup()
        os.environ.pop("LUTHOR_AB_TESTING_ENABLED", None)
        from luthor.config import reset_config

        reset_config()

    def _save_checkpoint(self, path: Path, seed: int) -> None:
        torch.manual_seed(seed)
        from luthor.config import get_config
        from luthor.jepa_model.world_model import WorldModel

        config = get_config()
        model = WorldModel(
            2,
            2,
            encoder_config=config.encoder,
            predictor_config=config.predictor,
            memory_config=config.memory,
            latent_dim=config.encoder.latent_dim,
        )
        torch.save({"state_dict": model.state_dict()}, path)

    def test_header_selects_different_models(self):
        default_response = self.client.post(
            "/embed",
            json={"observation": [1.0, 2.0]},
            headers={"X-Model-Version": "default"},
        )
        candidate_response = self.client.post(
            "/embed",
            json={"observation": [1.0, 2.0]},
            headers={"X-Model-Version": "candidate"},
        )
        self.assertEqual(default_response.status_code, 200)
        self.assertEqual(candidate_response.status_code, 200)
        self.assertNotEqual(
            default_response.json()["embedding"],
            candidate_response.json()["embedding"],
        )

    def test_logs_include_model_version(self):
        response = self.client.post(
            "/predict",
            json={"observation": [0.5, -1.0], "action": [0.2, 0.3], "mc_samples": 2},
            headers={"X-Model-Version": "candidate"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.mock_store.logged), 1)
        self.assertEqual(self.mock_store.logged[0]["model_version"], "candidate")
        self.assertIn("uncertainty", self.mock_store.logged[0]["metadata"])

    def test_ab_metrics_endpoint_returns_values(self):
        self.mock_store.metrics_rows = [
            {
                "model_version": "default",
                "calls": 5,
                "mean_uncertainty": 0.12,
                "mean_loss": None,
                "success_rate": None,
            },
            {
                "model_version": "candidate",
                "calls": 4,
                "mean_uncertainty": 0.08,
                "mean_loss": None,
                "success_rate": None,
            },
        ]

        response = self.client.get("/ab/metrics")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["window_hours"], 24)
        self.assertEqual(payload["versions"]["default"]["calls"], 5)
        self.assertEqual(payload["versions"]["candidate"]["calls"], 4)
        self.assertEqual(payload["winner"], "candidate")

    def test_ab_header_ignored_when_disabled(self):
        self.config.ab_testing.enabled = False
        from luthor.api.services import JEPAService

        self.client.app.state.jepa_service = JEPAService(self.config)

        first = self.client.post(
            "/embed",
            json={"observation": [1.0, 2.0]},
            headers={"X-Model-Version": "default"},
        )
        second = self.client.post(
            "/embed",
            json={"observation": [1.0, 2.0]},
            headers={"X-Model-Version": "candidate"},
        )
        self.assertEqual(first.json()["embedding"], second.json()["embedding"])
        self.assertEqual(self.mock_store.logged[-1]["model_version"], "default")


class _MockLogStore:
    def __init__(self):
        self.logged: list[dict] = []
        self.metrics_rows: list[dict] = []

    def ping(self) -> bool:
        return True

    def ensure_schema(self) -> None:
        return None

    def log_inference(self, **kwargs) -> int:
        self.logged.append(kwargs)
        return len(self.logged)

    def log_active_learning_round(self, **kwargs) -> int:
        return 1

    def fetch_ab_metrics(self, **kwargs):
        return self.metrics_rows


class _MockEmbeddingStore:
    def ping(self) -> bool:
        return True

    def add_embedding(self, embedding_id, embedding, metadata=None) -> None:
        return None


if __name__ == "__main__":
    unittest.main()
