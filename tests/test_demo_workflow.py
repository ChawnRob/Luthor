import os
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.demo_workflow import (
    check_mcp_availability,
    run_demo_workflow,
)
from luthor.llm_provider import ToolCompletionResult


class DemoWorkflowTests(unittest.TestCase):
    def setUp(self):
        os.environ["LUTHOR_MCP_ENABLED"] = "true"
        os.environ["LUTHOR_MCP_YTDLP_ENABLED"] = "true"
        from luthor.config import reset_config
        from luthor.mcp.registry import reset_mcp_registry

        reset_config()
        reset_mcp_registry()

    def tearDown(self):
        from luthor.config import reset_config
        from luthor.demo_workflow import reset_demo_tasks
        from luthor.mcp.registry import reset_mcp_registry

        reset_config()
        reset_mcp_registry()
        reset_demo_tasks()

    def test_check_mcp_availability_requires_active_connector(self):
        from luthor.mcp.registry import MCPRegistry

        registry = MCPRegistry()
        for name in registry.config.tools:
            registry.config.tools[name].enabled = False

        ok, message, _ = check_mcp_availability(registry)
        self.assertFalse(ok)
        self.assertIn("No MCP connectors", message)

    @patch("luthor.mcp.registry.MCPRegistry.call_tool", new_callable=AsyncMock)
    def test_run_demo_workflow_completes_with_mocked_tools(self, mock_call_tool):
        import asyncio

        from luthor.mcp.registry import MCPRegistry
        from luthor.orchestrator import MCPOrchestrator

        mock_call_tool.return_value = {"result": {"title": "Podcast IA", "duration": 600}}

        registry = MCPRegistry()
        registry.config.tools["ytdlp"].enabled = True

        mock_llm = MagicMock()
        mock_llm.complete_with_tools.return_value = ToolCompletionResult(
            content=None,
            tool_calls=[
                {
                    "id": "1",
                    "name": "ytdlp_extract_info",
                    "arguments": {"url": "https://youtube.com/watch?v=demo"},
                }
            ],
        )
        mock_llm.complete.return_value = "Synthèse générée."

        orchestrator = MCPOrchestrator(registry=registry, llm=mock_llm)

        with tempfile.TemporaryDirectory() as tmpdir:
            summary = asyncio.run(
                run_demo_workflow(
                    "Synthèse podcast IA",
                    orchestrator=orchestrator,
                    registry=registry,
                    output_dir=tmpdir,
                    run_id="testrun",
                )
            )

        self.assertTrue(summary.success)
        self.assertEqual(len(summary.steps), 1)
        self.assertEqual(summary.steps[0].tool_name, "ytdlp_extract_info")
        self.assertIn("Synthèse", summary.final_summary)


if __name__ == "__main__":
    unittest.main()
