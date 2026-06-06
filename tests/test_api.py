import os
import sys
import unittest
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


class MockEmbeddingStore:
    def ping(self) -> bool:
        return True

    def add_embedding(self, embedding_id, embedding, metadata=None) -> None:
        return None

    def get_embedding(self, embedding_id: str):
        return {
            "embedding_id": embedding_id,
            "embedding": [0.0, 0.0],
            "metadata": {},
        }


class ApiTests(unittest.TestCase):
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

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["model_loaded"])

    def test_embed(self):
        response = self.client.post("/embed", json={"observation": [1.0, 2.0]})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["latent_dim"], 4)
        self.assertEqual(len(payload["embedding"]), 4)
        self.assertTrue(payload["embedding_id"])

    def test_predict(self):
        response = self.client.post(
            "/predict",
            json={"observation": [0.5, -1.0], "action": [0.2, 0.3], "mc_samples": 2},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["predicted_latent"]), 4)
        self.assertIn("uncertainty", payload)

    def test_active_learn(self):
        response = self.client.post(
            "/active_learn",
            json={"num_rounds": 1, "pool_size": 4, "query_batch_size": 2},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["rounds"]), 1)
        self.assertIn("final_mean_loss", payload)


if __name__ == "__main__":
    unittest.main()
