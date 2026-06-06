import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class MockInferenceLogStore:
    def ping(self) -> bool:
        return True

    def log_inference(self, **kwargs) -> int:
        return 1

    def log_active_learning_round(self, **kwargs) -> int:
        return 1

    def list_inference_logs(self, **kwargs):
        return [], 0

    def list_tool_sync(self):
        return []

    def record_tool_sync(self, *args, **kwargs) -> None:
        return None


class MockEmbeddingStore:
    def ping(self) -> bool:
        return True

    def add_embedding(self, *args, **kwargs) -> None:
        return None


class MockUserStore:
    def ensure_schema(self) -> None:
        return None

    def upsert_from_jwt(self, **kwargs):
        from luthor.api.user_store import UserRecord

        return UserRecord(
            id=kwargs["user_id"],
            email=kwargs["email"],
            name=kwargs.get("name"),
            quota_tier="free",
            usage_count=0,
            subscription_status="active",
            storage_used_mb=0.0,
            mfa_enabled=False,
        )

    def get_daily_api_calls(self, user_id: str, usage_date=None) -> int:
        return 0

    def get_monthly_complex_tasks(self, user_id: str, month_start=None) -> int:
        return 0

    def increment_api_call(self, user_id: str, weight: int = 1) -> int:
        return weight

    def increment_complex_task(self, user_id: str) -> int:
        return 1

    def list_tool_sync(self):
        return []

    def record_tool_sync(self, *args, **kwargs) -> None:
        return None


class MCPE2ETests(unittest.TestCase):
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
        os.environ["LUTHOR_AUTH_REQUIRED"] = "false"
        os.environ["LUTHOR_MCP_ENABLED"] = "true"

        from luthor.config import reset_config

        reset_config()

        from luthor.api.main import create_app

        self.app = create_app()
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.client.app.state.log_store = MockInferenceLogStore()
        self.client.app.state.embedding_store = MockEmbeddingStore()
        self.client.app.state.user_store = MockUserStore()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        from luthor.config import reset_config

        reset_config()

    def test_mcp_tools_listing(self):
        response = self.client.get("/mcp/tools")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("connectors", payload)
        self.assertIn("tools", payload)

    @patch("luthor.api.routes.mcp.MCPOrchestrator.run", new_callable=AsyncMock)
    def test_mcp_orchestrate_end_to_end(self, mock_run):
        mock_run.return_value = MagicMock(
            message="done",
            used_tools=True,
            tool_calls=[],
        )
        response = self.client.post(
            "/mcp/orchestrate",
            json={"message": "Planifier une démo"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "done")

    def test_sync_tools_endpoint(self):
        response = self.client.get("/sync/tools")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("connectors", payload)
        self.assertIn("synced_at", payload)


if __name__ == "__main__":
    unittest.main()
