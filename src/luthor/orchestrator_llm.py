from __future__ import annotations

import logging
from typing import Any

from luthor.llm_provider import LLMConfig, LLMInterface, LLMProvider, ToolCompletionResult
from luthor.slm_fallback import complete as slm_complete

logger = logging.getLogger(__name__)


class ResilientOrchestratorLLM:
    """Primary cloud LLM with on-demand SmolLM3 fallback (no permanent local service)."""

    def __init__(self, primary: LLMInterface):
        self.primary = primary
        self.last_provider = "primary"

    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        try:
            self.last_provider = self.primary.config.provider.value
            return self.primary.complete(
                prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:
            logger.warning("Primary LLM failed, trying SmolLM fallback: %s", exc)
            self.last_provider = "smollm3"
            return slm_complete(prompt, system_prompt=system_prompt)

    def complete_with_tools(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ToolCompletionResult:
        try:
            self.last_provider = self.primary.config.provider.value
            return self.primary.complete_with_tools(
                prompt,
                tools=tools,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:
            logger.warning("Primary tool LLM failed, SmolLM direct answer fallback: %s", exc)
            self.last_provider = "smollm3"
            fallback_text = slm_complete(
                f"{prompt}\n\n(No external tools available — answer directly.)",
                system_prompt=system_prompt,
            )
            return ToolCompletionResult(content=fallback_text, tool_calls=[])

    @property
    def config(self) -> LLMConfig:
        return self.primary.config
