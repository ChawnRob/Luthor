from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from luthor.api.schemas import (
    MCPOrchestrateRequest,
    MCPOrchestrateResponse,
    MCPToolInfo,
    MCPToolsResponse,
)
from luthor.orchestrator import MCPOrchestrator

router = APIRouter(tags=["mcp"])


@router.get("/mcp/tools", response_model=MCPToolsResponse)
def list_mcp_tools(request: Request) -> MCPToolsResponse:
    registry = request.app.state.mcp_registry
    tools = [
        MCPToolInfo(
            name=tool["name"],
            type=tool.get("type", "mcp"),
            connector=tool["connector"],
            description=tool["description"],
            endpoint=tool["endpoint"],
        )
        for tool in registry.list_tools()
    ]
    return MCPToolsResponse(
        enabled=registry.config.enabled,
        connectors=registry.connector_status(),
        tools=tools,
    )


@router.post("/mcp/orchestrate", response_model=MCPOrchestrateResponse)
async def orchestrate_mcp_tools(
    payload: MCPOrchestrateRequest,
    request: Request,
) -> MCPOrchestrateResponse:
    orchestrator: MCPOrchestrator = request.app.state.orchestrator
    try:
        result = await orchestrator.run(payload.message, system_prompt=payload.system_prompt)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Orchestration failed: {exc}") from exc

    return MCPOrchestrateResponse(
        message=result.message,
        used_tools=result.used_tools,
        tool_calls=[
            {
                "tool_name": call.tool_name,
                "arguments": call.arguments,
                "result": call.result,
            }
            for call in result.tool_calls
        ],
    )
