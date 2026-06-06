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


class MockEmbeddingStore:
    def ping(self) -> bool:
        return True

    def add_embedding(self, embedding_id, embedding, metadata=None) -> None:
        return None


class DemoEndpointTests(unittest.TestCase):
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
        os.environ["LUTHOR_MCP_ENABLED"] = "true"
        os.environ["LUTHOR_MCP_YTDLP_ENABLED"] = "true"
        os.environ.pop("MISTRAL_API_KEY", None)

        from luthor.config import reset_config
        from luthor.demo_workflow import reset_demo_tasks
        from luthor.mcp.registry import MCPRegistry, reset_mcp_registry

        reset_config()
        reset_mcp_registry()
        reset_demo_tasks()

        from luthor.api.main import create_app
        from luthor.orchestrator import MCPOrchestrator

        self.app = create_app()
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.client.app.state.log_store = MockInferenceLogStore()
        self.client.app.state.embedding_store = MockEmbeddingStore()
        self.registry = MCPRegistry()
        self.registry.config.tools["ytdlp"].enabled = True
        self.client.app.state.mcp_registry = self.registry
        self.client.app.state.orchestrator = MCPOrchestrator(
            registry=self.registry,
            llm=MagicMock(),
        )

    def tearDown(self):
        self.client.__exit__(None, None, None)
        from luthor.config import reset_config
        from luthor.demo_workflow import reset_demo_tasks
        from luthor.mcp.registry import reset_mcp_registry

        reset_config()
        reset_mcp_registry()
        reset_demo_tasks()

    @patch("luthor.api.routes.demo.run_demo_workflow", new_callable=AsyncMock)
    def test_demo_full_sync_returns_summary(self, mock_run):
        from luthor.demo_workflow import DemoWorkflowSummary

        mock_run.return_value = DemoWorkflowSummary(
            run_id="abc",
            message="test",
            started_at="t0",
            finished_at="t1",
            duration_seconds=0.1,
            final_summary="done",
            used_tools=False,
            warnings=[],
            steps=[],
            output_dir="/tmp/demo",
            success=True,
        )

        response = self.client.post(
            "/demo/full",
            json={"message": "Court test démo", "async": False},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["summary"]["final_summary"], "done")

    def test_demo_full_rejects_when_mcp_disabled(self):
        for name in self.registry.config.tools:
            self.registry.config.tools[name].enabled = False

        response = self.client.post(
            "/demo/full",
            json={"message": "test"},
        )
        self.assertEqual(response.status_code, 400)

    def test_demo_ui_route(self):
        response = self.client.get("/demo-ui")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))


if __name__ == "__main__":
    unittest.main()
