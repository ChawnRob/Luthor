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


class MockEmbeddingStore:
    def ping(self) -> bool:
        return True

    def add_embedding(self, embedding_id, embedding, metadata=None) -> None:
        return None


class MCPConnectorTests(unittest.TestCase):
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
        os.environ["LUTHOR_MCP_N8N_ENABLED"] = "true"
        os.environ["LUTHOR_MCP_PENPOT_ENABLED"] = "true"
        os.environ["LUTHOR_MCP_APPFLOWY_ENABLED"] = "true"
        os.environ["LUTHOR_MCP_PLAUSIBLE_ENABLED"] = "true"
        os.environ["N8N_API_URL"] = "https://n8n.example.com"
        os.environ["N8N_API_KEY"] = "test-n8n-key"
        os.environ["PENPOT_API_URL"] = "https://penpot.example.com"
        os.environ["PENPOT_ACCESS_TOKEN"] = "test-penpot-token"
        os.environ["APPFLOWY_API_URL"] = "https://appflowy.example.com"
        os.environ["APPFLOWY_TOKEN"] = "test-appflowy-token"
        os.environ["PLAUSIBLE_API_URL"] = "https://plausible.example.com"
        os.environ["PLAUSIBLE_SITE_ID"] = "luthor.example.com"
        os.environ["PLAUSIBLE_TOKEN"] = "test-plausible-token"
        os.environ.pop("MISTRAL_API_KEY", None)

        from luthor.config import reset_config
        from luthor.mcp.registry import reset_mcp_registry

        reset_config()
        reset_mcp_registry()

        from luthor.api.main import create_app
        from luthor.mcp.registry import MCPRegistry
        from luthor.orchestrator import MCPOrchestrator

        self.app = create_app()
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.client.app.state.log_store = MockInferenceLogStore()
        self.client.app.state.embedding_store = MockEmbeddingStore()
        self.registry = MCPRegistry()
        self.client.app.state.mcp_registry = self.registry
        self.client.app.state.orchestrator = MCPOrchestrator(registry=self.registry, llm=MagicMock())

    def tearDown(self):
        self.client.__exit__(None, None, None)
        from luthor.config import reset_config
        from luthor.mcp.registry import reset_mcp_registry

        reset_config()
        reset_mcp_registry()

    def test_mcp_tools_lists_all_definitions_when_enabled(self):
        response = self.client.get("/mcp/tools")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["enabled"])
        self.assertEqual(len(payload["tools"]), 10)
        names = {tool["name"] for tool in payload["tools"]}
        self.assertIn("n8n_trigger_workflow", names)
        self.assertIn("plausible_get_stats", names)

    @patch("luthor.mcp.http_client.MCPHttpClient.request", new_callable=AsyncMock)
    def test_n8n_list_workflows_endpoint(self, mock_request):
        mock_request.return_value = {"data": [{"id": "wf-1", "name": "CRM sync"}]}
        response = self.client.get("/tools/n8n")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["workflows"][0]["id"], "wf-1")

    @patch("luthor.mcp.http_client.MCPHttpClient.request", new_callable=AsyncMock)
    def test_n8n_trigger_endpoint(self, mock_request):
        mock_request.return_value = {"executionId": "exec-42"}
        response = self.client.post(
            "/tools/n8n",
            json={"workflow_id": "wf-1", "payload": {"email": "ops@luthor.ai"}},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"]["executionId"], "exec-42")

    @patch("luthor.mcp.http_client.MCPHttpClient.request", new_callable=AsyncMock)
    def test_penpot_create_file(self, mock_request):
        mock_request.return_value = {"id": "file-9"}
        response = self.client.post(
            "/tools/penpot",
            json={"action": "create_file", "project_id": "proj-1", "name": "Landing"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"]["id"], "file-9")

    @patch("luthor.mcp.http_client.MCPHttpClient.request", new_callable=AsyncMock)
    def test_appflowy_search_pages(self, mock_request):
        mock_request.return_value = {"pages": [{"id": "p1", "title": "Runbook"}]}
        response = self.client.post(
            "/tools/appflowy",
            json={"action": "search_pages", "query": "runbook"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("pages", response.json()["result"])

    @patch("luthor.mcp.http_client.MCPHttpClient.request", new_callable=AsyncMock)
    def test_plausible_track_event(self, mock_request):
        mock_request.return_value = {"ok": True}
        response = self.client.post(
            "/tools/plausible",
            json={"action": "track_event", "event_name": "agent_run", "props": {"source": "luthor"}},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["result"]["ok"])

    @patch("luthor.mcp.http_client.MCPHttpClient.request", new_callable=AsyncMock)
    def test_registry_call_tool_routes_to_connector(self, mock_request):
        mock_request.return_value = {"visitors": 120}
        import asyncio

        result = asyncio.run(
            self.registry.call_tool(
                "plausible_get_stats",
                {"period": "7d", "metrics": ["visitors"]},
            )
        )
        self.assertEqual(result["result"]["visitors"], 120)

    def test_orchestrator_executes_tool_calls(self):
        from luthor.llm_provider import ToolCompletionResult
        from luthor.orchestrator import MCPOrchestrator

        mock_llm = MagicMock()
        mock_llm.complete_with_tools.return_value = ToolCompletionResult(
            content=None,
            tool_calls=[
                {
                    "id": "call-1",
                    "name": "plausible_track_event",
                    "arguments": {"event_name": "mcp_test"},
                }
            ],
        )
        mock_llm.complete.return_value = "Event tracked successfully."

        orchestrator = MCPOrchestrator(registry=self.registry, llm=mock_llm)
        with patch(
            "luthor.mcp.http_client.MCPHttpClient.request",
            new_callable=AsyncMock,
            return_value={"ok": True},
        ):
            import asyncio

            result = asyncio.run(orchestrator.run("Track an MCP test event in analytics"))
        self.assertTrue(result.used_tools)
        self.assertEqual(result.tool_calls[0].tool_name, "plausible_track_event")
        self.assertIn("tracked", result.message.lower())


if __name__ == "__main__":
    unittest.main()
