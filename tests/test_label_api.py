import os
import sys
import unittest
from unittest import mock

import torch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class MockHumanLabelStore:
    def ping(self) -> bool:
        return True

    def save_label(self, sample_id, correct_outcome) -> int:
        return 1

    def get_label(self, sample_id: str):
        return None


class MockInferenceLogStore:
    def ping(self) -> bool:
        return True

    def log_inference(self, **kwargs) -> int:
        return 1

    def log_active_learning_round(self, **kwargs) -> int:
        return 1


class MockEmbeddingStore:
    def ping(self) -> bool:
        return True

    def add_embedding(self, embedding_id, embedding, metadata=None) -> None:
        return None


class LabelApiTests(unittest.TestCase):
    def setUp(self):
        os.environ["LUTHOR_ENCODER_LATENT_DIM"] = "4"
        os.environ["LUTHOR_ENCODER_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_ENCODER_NUM_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_PREDICTOR_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_USE_ATTENTION"] = "true"
        os.environ["LUTHOR_PLANNER_LR"] = "0.01"
        os.environ["LUTHOR_HUMAN_IN_LOOP"] = "false"
        os.environ["LUTHOR_WEATHER_ENABLED"] = "true"

        from luthor.config import reset_config

        reset_config()

        from luthor.api.main import create_app

        self.app = create_app()
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.client.app.state.log_store = MockInferenceLogStore()
        self.client.app.state.embedding_store = MockEmbeddingStore()
        self.client.app.state.label_store = MockHumanLabelStore()

    def tearDown(self):
        self.client.app.state.pending_registry.clear()
        self.client.__exit__(None, None, None)
        from luthor.config import reset_config

        reset_config()

    def test_submit_label_for_pending_sample(self):
        from luthor.active_learning.pending_labels import PendingSample

        registry = self.client.app.state.pending_registry
        registry.register(
            PendingSample(
                sample_id="sample-1",
                observation=torch.tensor([1.0, 2.0]),
                action=torch.tensor([0.1, 0.2]),
            )
        )

        response = self.client.post(
            "/label",
            json={
                "sample_id": "sample-1",
                "correct_outcome": {"next_observation": [1.5, 2.5]},
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["stored"])

    def test_submit_label_unknown_sample_returns_404(self):
        response = self.client.post(
            "/label",
            json={
                "sample_id": "missing",
                "correct_outcome": {"next_observation": [0.0, 0.0]},
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_list_pending_labels(self):
        from luthor.active_learning.pending_labels import PendingSample

        registry = self.client.app.state.pending_registry
        registry.register(
            PendingSample(
                sample_id="pending-1",
                observation=torch.tensor([0.0, 0.0]),
                action={"action_type": "call_tool", "tool_name": "weather", "tool_args": {}},
                metadata={"requires_human_relevance": True},
            )
        )

        response = self.client.get("/label/pending")
        self.assertEqual(response.status_code, 200)
        pending = response.json()["pending"]
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["sample_id"], "pending-1")

    @mock.patch("luthor.api.routes.tools.get_weather")
    def test_weather_endpoint(self, mock_get_weather):
        mock_get_weather.return_value = {
            "latitude": 48.0,
            "longitude": 2.0,
            "temperature_c": 15.0,
            "wind_speed_kmh": 5.0,
            "weather_code": 1,
            "source": "open-meteo",
        }

        response = self.client.get("/tools/weather", params={"latitude": 48.0, "longitude": 2.0})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["temperature_c"], 15.0)


if __name__ == "__main__":
    unittest.main()
