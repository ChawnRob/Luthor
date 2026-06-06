import base64
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


class MCPMediaConnectorTests(unittest.TestCase):
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
        os.environ["LUTHOR_MCP_WHISPER_ENABLED"] = "true"
        os.environ["LUTHOR_MCP_YTDLP_ENABLED"] = "true"
        os.environ["LUTHOR_MCP_FOOOCUS_ENABLED"] = "true"
        os.environ["LUTHOR_MCP_CALCOM_ENABLED"] = "true"
        os.environ["WHISPER_MODEL_SIZE"] = "tiny"
        os.environ["WHISPER_DEVICE"] = "cpu"
        os.environ["FOOOCUS_API_URL"] = "http://fooocus.example.com:8888"
        os.environ["CALCOM_API_URL"] = "https://cal.example.com"
        os.environ["CALCOM_API_KEY"] = "cal-test-key"
        os.environ["CALCOM_EVENT_TYPE_ID"] = "42"
        os.environ.pop("MISTRAL_API_KEY", None)

        from luthor.config import reset_config
        from luthor.mcp.registry import MCPRegistry, reset_mcp_registry

        reset_config()
        reset_mcp_registry()

        from luthor.api.main import create_app
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

    def test_mcp_tools_includes_media_connectors(self):
        response = self.client.get("/mcp/tools")
        self.assertEqual(response.status_code, 200)
        names = {tool["name"] for tool in response.json()["tools"]}
        self.assertIn("whisper_transcribe", names)
        self.assertIn("ytdlp_download_media", names)
        self.assertIn("fooocus_generate_image", names)
        self.assertIn("calcom_create_booking", names)

    @patch("luthor.mcp.whisper_connector.WhisperConnector._transcribe_file")
    def test_transcribe_endpoint_with_b64(self, mock_transcribe):
        mock_transcribe.return_value = "bonjour luthor"
        audio_b64 = base64.b64encode(b"fake-audio").decode("ascii")
        response = self.client.post(
            "/tools/transcribe",
            json={"audio_b64": audio_b64, "language": "fr"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["text"], "bonjour luthor")

    @patch("luthor.mcp.ytdlp_connector.YtDlpConnector._extract_info_sync")
    def test_download_extract_info(self, mock_extract):
        mock_extract.return_value = {
            "title": "Demo",
            "duration": 120,
            "description": "test",
            "uploader": "luthor",
            "webpage_url": "https://youtube.com/watch?v=abc",
        }
        response = self.client.post(
            "/tools/download",
            json={
                "url": "https://youtube.com/watch?v=abc",
                "action": "extract_info",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"]["title"], "Demo")

    def test_download_media_rejects_disallowed_domain(self):
        import asyncio

        with self.assertRaises(ValueError) as ctx:
            asyncio.run(self.registry.ytdlp.download_media("https://evil.example/video"))
        self.assertIn("Domain not allowed", str(ctx.exception))

    @patch("luthor.mcp.http_client.MCPHttpClient.request", new_callable=AsyncMock)
    def test_generate_image_endpoint(self, mock_request):
        mock_request.side_effect = [
            {"status": "ok"},
            {"image_url": "http://fooocus.example.com/out.png"},
        ]
        response = self.client.post(
            "/tools/generate_image",
            json={"prompt": "A minimal SME dashboard icon"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("out.png", response.json()["image_url"])

    @patch("luthor.mcp.http_client.MCPHttpClient.request", new_callable=AsyncMock)
    def test_booking_and_availability(self, mock_request):
        mock_request.side_effect = [
            {"slots": ["09:00", "10:00"]},
            {"id": "booking-1", "status": "PENDING", "uid": "uid-1"},
        ]
        availability = self.client.get("/tools/availability?date=2026-06-10")
        self.assertEqual(availability.status_code, 200)
        self.assertEqual(len(availability.json()["result"]["slots"]), 2)

        booking = self.client.post(
            "/tools/booking",
            json={
                "start_time": "2026-06-10T09:00:00Z",
                "end_time": "2026-06-10T09:30:00Z",
                "name": "Alice",
                "email": "alice@example.com",
            },
        )
        self.assertEqual(booking.status_code, 200)
        self.assertEqual(booking.json()["result"]["status"], "PENDING")

    @patch("luthor.mcp.whisper_connector.WhisperConnector._transcribe_file")
    def test_registry_whisper_tool(self, mock_transcribe):
        mock_transcribe.return_value = "hello world"
        import asyncio

        result = asyncio.run(
            self.registry.call_tool(
                "whisper_transcribe",
                {"audio_b64": base64.b64encode(b"x").decode("ascii")},
            )
        )
        self.assertEqual(result["result"]["text"], "hello world")


if __name__ == "__main__":
    unittest.main()
