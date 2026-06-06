import os
import sys
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class MockInferenceLogStore:
    def ping(self) -> bool:
        return True

    def ensure_schema(self) -> None:
        return None

    def log_inference(self, **kwargs) -> int:
        return 1

    def log_active_learning_round(self, **kwargs) -> int:
        return 1

    def list_inference_logs(self, **kwargs):
        return (
            [
                {
                    "id": 1,
                    "endpoint": "/predict",
                    "request_payload": {"observation": [1.0]},
                    "response_payload": {"uncertainty": 0.2},
                    "metadata": {},
                    "model_version": "default",
                    "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
                }
            ],
            1,
        )


class MockEmbeddingStore:
    def ping(self) -> bool:
        return True

    def add_embedding(self, embedding_id, embedding, metadata=None) -> None:
        return None

    def get_embedding(self, embedding_id: str):
        return None


class DashboardApiTests(unittest.TestCase):
    def setUp(self):
        os.environ["LUTHOR_ENCODER_LATENT_DIM"] = "4"
        os.environ["LUTHOR_ENCODER_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_ENCODER_NUM_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_PREDICTOR_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_USE_ATTENTION"] = "true"
        os.environ["LUTHOR_PLANNER_LR"] = "0.01"
        os.environ["LUTHOR_AL_ROUNDS"] = "1"
        os.environ["LUTHOR_AL_POOL_SIZE"] = "4"
        os.environ["LUTHOR_AL_QUERY_BATCH"] = "2"
        os.environ["LUTHOR_AL_MC_SAMPLES"] = "2"
        os.environ["LUTHOR_AL_TRAIN_STEPS"] = "1"
        os.environ["LUTHOR_AB_TESTING_ENABLED"] = "false"

        from luthor.config import reset_config

        reset_config()

        from luthor.api.main import create_app

        self.app = create_app()
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.client.app.state.log_store = MockInferenceLogStore()
        self.client.app.state.embedding_store = MockEmbeddingStore()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        from luthor.config import reset_config

        reset_config()

    def test_list_logs(self):
        response = self.client.get("/logs?page=1&page_size=10")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total"], 1)
        self.assertEqual(len(payload["items"]), 1)
        self.assertEqual(payload["items"][0]["endpoint"], "/predict")

    def test_read_config(self):
        response = self.client.get("/config")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("connectors", payload)
        self.assertIn("message", payload)
        self.assertIn("n8n", payload["connectors"])


if __name__ == "__main__":
    unittest.main()
