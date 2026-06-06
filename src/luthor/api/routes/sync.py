from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

from luthor.api.schemas import ToolSyncItem, ToolSyncResponse
from luthor.api.user_store import UserStore

router = APIRouter(prefix="/sync", tags=["sync"])


@router.get("/tools", response_model=ToolSyncResponse)
def sync_tools_status(request: Request) -> ToolSyncResponse:
    registry = request.app.state.mcp_registry
    user_store: UserStore = request.app.state.user_store

    stored = {row["connector_name"]: row for row in user_store.list_tool_sync()}
    tools_by_connector: dict[str, int] = {}
    for tool in registry.list_tools():
        connector = tool.get("connector", "unknown")
        tools_by_connector[connector] = tools_by_connector.get(connector, 0) + 1

    connectors_status = registry.connector_status()
    items: list[ToolSyncItem] = []

    for name, enabled in connectors_status.items():
        live_status = "online" if enabled else "offline"
        user_store.record_tool_sync(name, live_status, {"enabled": enabled})
        stored_row = stored.get(name, {})
        last_sync = stored_row.get("last_sync_at")
        if hasattr(last_sync, "isoformat"):
            last_sync = last_sync.isoformat()

        items.append(
            ToolSyncItem(
                connector=name,
                enabled=enabled,
                status=live_status,
                last_sync_at=last_sync if isinstance(last_sync, str) else datetime.now(timezone.utc).isoformat(),
                tools_count=tools_by_connector.get(name, 0),
            )
        )

    return ToolSyncResponse(
        connectors=sorted(items, key=lambda item: item.connector),
        synced_at=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/tools/{connector_name}", response_model=ToolSyncItem)
def sync_connector(connector_name: str, request: Request) -> ToolSyncItem:
    registry = request.app.state.mcp_registry
    user_store: UserStore = request.app.state.user_store

    status_map = registry.connector_status()
    if connector_name not in status_map:
        raise HTTPException(status_code=404, detail=f"Unknown connector: {connector_name}")

    enabled = status_map[connector_name]
    live_status = "online" if enabled else "offline"
    user_store.record_tool_sync(connector_name, live_status, {"manual_sync": True})

    tools_count = sum(
        1 for tool in registry.list_tools() if tool.get("connector") == connector_name
    )

    return ToolSyncItem(
        connector=connector_name,
        enabled=enabled,
        status=live_status,
        last_sync_at=datetime.now(timezone.utc).isoformat(),
        tools_count=tools_count,
    )
