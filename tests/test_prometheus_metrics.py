import os
import sys
import unittest
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.api.metrics import parse_counter_total


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


class PrometheusMetricsTests(unittest.TestCase):
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
        os.environ.pop("LUTHOR_PROMETHEUS_PUSH_GATEWAY", None)

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

    def _metrics_text(self) -> str:
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response.headers.get("content-type", ""))
        return response.text

    def test_metrics_endpoint_exposes_required_series(self):
        text = self._metrics_text()
        for metric_name in (
            "http_requests_total",
            "http_request_duration_seconds",
            "jepa_inference_latency",
            "active_learning_rounds_total",
            "model_version_requests_total",
        ):
            self.assertIn(f"# TYPE {metric_name}", text)

    def test_http_requests_total_increments(self):
        before = parse_counter_total(self._metrics_text(), "http_requests_total")
        self.client.get("/health")
        after = parse_counter_total(self._metrics_text(), "http_requests_total")
        self.assertGreater(after, before)

    def test_jepa_and_model_version_metrics_increment(self):
        before_jepa = parse_counter_total(
            self._metrics_text(),
            "jepa_inference_latency_count",
        )
        before_versions = parse_counter_total(
            self._metrics_text(),
            "model_version_requests_total",
            'endpoint="/embed"',
        )

        response = self.client.post("/embed", json={"observation": [1.0, 2.0]})
        self.assertEqual(response.status_code, 200)

        text = self._metrics_text()
        after_jepa = parse_counter_total(text, "jepa_inference_latency_count")
        after_versions = parse_counter_total(
            text,
            "model_version_requests_total",
            'endpoint="/embed"',
        )

        self.assertGreater(after_jepa, before_jepa)
        self.assertGreater(after_versions, before_versions)

    def test_active_learning_rounds_increment(self):
        before = parse_counter_total(self._metrics_text(), "active_learning_rounds_total")
        response = self.client.post(
            "/active_learn",
            json={"num_rounds": 1, "pool_size": 4, "query_batch_size": 2},
        )
        self.assertEqual(response.status_code, 200)
        after = parse_counter_total(self._metrics_text(), "active_learning_rounds_total")
        self.assertGreaterEqual(after, before + 1)

    def test_push_gateway_starts_when_configured(self):
        os.environ["LUTHOR_PROMETHEUS_PUSH_GATEWAY"] = "http://pushgateway:9091"
        with unittest.mock.patch("luthor.api.metrics.push_to_gateway") as mock_push:
            from luthor.api.metrics import start_push_gateway_if_configured, stop_push_gateway

            start_push_gateway_if_configured()
            stop_push_gateway()
            self.assertTrue(mock_push.called)


if __name__ == "__main__":
    unittest.main()
