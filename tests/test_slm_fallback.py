import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.orchestrator_llm import ResilientOrchestratorLLM
from luthor.slm_fallback import reset_for_tests


class SLMFallbackTests(unittest.TestCase):
    def tearDown(self):
        reset_for_tests()

    @patch("luthor.orchestrator_llm.slm_complete", return_value="fallback answer")
    def test_resilient_llm_uses_fallback_on_primary_failure(self, mock_slm):
        primary = MagicMock()
        primary.config.provider.value = "mistral"
        primary.complete.side_effect = RuntimeError("cloud down")

        llm = ResilientOrchestratorLLM(primary)
        result = llm.complete("hello")
        self.assertEqual(result, "fallback answer")
        self.assertEqual(llm.last_provider, "smollm3")

    @patch("luthor.orchestrator_llm.slm_complete", return_value="no tools answer")
    def test_resilient_llm_tool_fallback_returns_text(self, mock_slm):
        primary = MagicMock()
        primary.config.provider.value = "mistral"
        primary.complete_with_tools.side_effect = RuntimeError("rate limit")

        llm = ResilientOrchestratorLLM(primary)
        result = llm.complete_with_tools("plan task", tools=[{"type": "function"}])
        self.assertEqual(result.content, "no tools answer")
        self.assertEqual(result.tool_calls, [])


if __name__ == "__main__":
    unittest.main()
