import os
import sys
import unittest

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class LabelUiTests(unittest.TestCase):
    def setUp(self):
        os.environ["LUTHOR_ENCODER_LATENT_DIM"] = "4"
        os.environ["LUTHOR_ENCODER_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_ENCODER_NUM_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_PREDICTOR_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_USE_ATTENTION"] = "true"
        os.environ["LUTHOR_PLANNER_LR"] = "0.01"
        os.environ["LUTHOR_AB_TESTING_ENABLED"] = "false"

        from luthor.config import reset_config

        reset_config()
        from luthor.api.main import create_app

        self.app = create_app()
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.client.app.state.log_store = _MockLogStore()
        self.client.app.state.embedding_store = _MockEmbeddingStore()

    def tearDown(self):
        self.client.app.state.pending_registry.clear()
        self.client.__exit__(None, None, None)
        from luthor.config import reset_config

        reset_config()

    def test_label_ui_route_served(self):
        response = self.client.get("/label-ui")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Luthor", response.text)

    def test_label_submit_flow(self):
        import torch
        from luthor.active_learning.pending_labels import PendingSample

        registry = self.client.app.state.pending_registry
        registry.register(
            PendingSample(
                sample_id="inv-1",
                observation=torch.tensor([1.0, 2.0, 3.0, 0.0, 0.0, 0.0]),
                action=torch.tensor([0.1, 0.2, 0.3]),
                metadata={"environment": "inventory"},
            )
        )

        response = self.client.post(
            "/label",
            json={
                "sample_id": "inv-1",
                "correct_outcome": {"next_observation": [1.0, 2.0, 2.0, 5.0, 4.0, 1.0]},
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["stored"])


class _MockLogStore:
    def ping(self) -> bool:
        return True

    def ensure_schema(self) -> None:
        return None

    def log_inference(self, **kwargs) -> int:
        return 1

    def log_active_learning_round(self, **kwargs) -> int:
        return 1


class _MockEmbeddingStore:
    def ping(self) -> bool:
        return True

    def add_embedding(self, embedding_id, embedding, metadata=None) -> None:
        return None


if __name__ == "__main__":
    unittest.main()
