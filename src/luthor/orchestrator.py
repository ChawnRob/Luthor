from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from luthor.llm_provider import LLMConfig, LLMInterface, LLMProvider, LLMProviderFactory
from luthor.mcp.registry import MCPRegistry, get_mcp_registry
from luthor.orchestrator_llm import ResilientOrchestratorLLM


@dataclass
class ToolCallResult:
    tool_name: str
    arguments: dict[str, Any]
    result: dict[str, Any]


@dataclass
class OrchestrationResult:
    message: str
    tool_calls: list[ToolCallResult] = field(default_factory=list)
    used_tools: bool = False


class MCPOrchestrator:
    """Routes user requests through Mistral function calling to MCP tools."""

    def __init__(
        self,
        registry: MCPRegistry | None = None,
        llm: LLMInterface | None = None,
    ):
        self.registry = registry or get_mcp_registry()
        self._llm = llm

    @property
    def llm(self) -> ResilientOrchestratorLLM | LLMInterface:
        if self._llm is None:
            primary = self._build_mistral_llm()
            self._llm = ResilientOrchestratorLLM(primary)
        return self._llm

    @staticmethod
    def _build_mistral_llm() -> LLMInterface:
        provider = os.getenv("LUTHOR_MCP_LLM_PROVIDER", "mistral").lower()
        if provider != "mistral":
            return LLMInterface()

        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY is required for MCP orchestration")

        config = LLMConfig(
            provider=LLMProvider.MISTRAL,
            model=os.getenv("LUTHOR_MCP_MODEL", "mistral-small-latest"),
            api_key=api_key,
            api_base="https://api.mistral.ai/v1",
            temperature=float(os.getenv("LUTHOR_LLM_TEMPERATURE", "0.2")),
            max_tokens=int(os.getenv("LUTHOR_LLM_MAX_TOKENS", "2048")),
            timeout=int(os.getenv("LUTHOR_LLM_TIMEOUT", "30")),
        )
        return LLMInterface(config=config)

    async def plan_tools(
        self,
        user_message: str,
        system_prompt: str | None = None,
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """Return LLM text (if any) and planned tool calls without executing them."""
        tools = self.registry.get_function_tools()
        if not tools:
            return "No MCP tools are enabled. Configure connectors in params.yaml and .env.", []

        default_system = (
            "You are the LUTHOR agent orchestrator. "
            "Choose the best MCP tool when external automation, design, memory, or analytics is needed. "
            "Otherwise answer directly without calling tools."
        )
        completion = self.llm.complete_with_tools(
            prompt=user_message,
            tools=tools,
            system_prompt=system_prompt or default_system,
        )
        return completion.content, list(completion.tool_calls)

    async def summarize_tool_results(
        self,
        user_message: str,
        tool_results: list[ToolCallResult],
    ) -> str:
        summary_prompt = (
            f"User request: {user_message}\n\n"
            f"Tool results: {json.dumps([item.result for item in tool_results], ensure_ascii=False)}\n\n"
            "Summarize the outcome for the user in concise French or English matching the request."
        )
        return self.llm.complete(summary_prompt)

    async def run(self, user_message: str, system_prompt: str | None = None) -> OrchestrationResult:
        content, planned_calls = await self.plan_tools(user_message, system_prompt=system_prompt)
        if not planned_calls:
            return OrchestrationResult(
                message=content or "No response generated.",
                used_tools=False,
            )

        tool_results: list[ToolCallResult] = []
        for call in planned_calls:
            arguments = call.get("arguments", {})
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            result = await self.registry.call_tool(call["name"], arguments)
            tool_results.append(
                ToolCallResult(
                    tool_name=call["name"],
                    arguments=arguments,
                    result=result,
                )
            )

        final_message = await self.summarize_tool_results(user_message, tool_results)
        return OrchestrationResult(
            message=final_message,
            tool_calls=tool_results,
            used_tools=True,
        )


def get_orchestrator() -> MCPOrchestrator:
    return MCPOrchestrator()
