from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from luthor.config import MCPConfig, get_config
from luthor.mcp.appflowy_connector import AppFlowyConnector
from luthor.mcp.calcom_connector import CalComConnector
from luthor.mcp.fooocus_connector import FooocusConnector
from luthor.mcp.n8n_connector import N8nConnector
from luthor.mcp.penpot_connector import PenpotConnector
from luthor.mcp.plausible_connector import PlausibleConnector
from luthor.mcp.whisper_connector import WhisperConnector
from luthor.mcp.ytdlp_connector import YtDlpConnector

_TOOLS_PATH = Path(__file__).resolve().parent / "mcp_tools.json"
_registry: MCPRegistry | None = None


class MCPRegistry:
    """Loads MCP tool definitions and routes calls to connectors."""

    def __init__(self, mcp_config: MCPConfig | None = None):
        self.config = mcp_config or get_config().mcp
        self._tools = self._load_tools()
        n8n_cfg = self.config.tools["n8n"]
        penpot_cfg = self.config.tools["penpot"]
        appflowy_cfg = self.config.tools["appflowy"]
        plausible_cfg = self.config.tools["plausible"]
        whisper_cfg = self.config.tools["whisper"]
        ytdlp_cfg = self.config.tools["ytdlp"]
        fooocus_cfg = self.config.tools["fooocus"]
        calcom_cfg = self.config.tools["calcom"]

        self.n8n = N8nConnector(
            api_url=n8n_cfg.url or None,
            api_key=n8n_cfg.api_key or None,
        )
        self.penpot = PenpotConnector(
            api_url=penpot_cfg.url or None,
            access_token=penpot_cfg.token or None,
        )
        self.appflowy = AppFlowyConnector(
            api_url=appflowy_cfg.url or None,
            token=appflowy_cfg.token or None,
        )
        self.plausible = PlausibleConnector(
            api_url=plausible_cfg.url or None,
            site_id=plausible_cfg.site_id or None,
            token=plausible_cfg.token or None,
        )
        self.whisper = WhisperConnector(
            model_size=whisper_cfg.model,
            device=whisper_cfg.device,
        )
        self.ytdlp = YtDlpConnector(config=ytdlp_cfg)
        self.fooocus = FooocusConnector(
            api_url=fooocus_cfg.url or None,
            api_key=fooocus_cfg.api_key or None,
        )
        self.calcom = CalComConnector(
            api_url=calcom_cfg.url or None,
            api_key=calcom_cfg.api_key or None,
            event_type_id=calcom_cfg.event_type_id or None,
        )

    @staticmethod
    def _load_tools() -> list[dict[str, Any]]:
        with _TOOLS_PATH.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        return list(payload.get("tools", []))

    def list_tools(self) -> list[dict[str, Any]]:
        """Return tool metadata for debugging and orchestration."""
        enabled_connectors = self._enabled_connectors()
        return [
            tool
            for tool in self._tools
            if tool.get("connector") in enabled_connectors
        ]

    def get_function_tools(self) -> list[dict[str, Any]]:
        """Return OpenAI/Mistral-compatible function definitions."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                },
            }
            for tool in self.list_tools()
        ]

    def _enabled_connectors(self) -> set[str]:
        if not self.config.enabled:
            return set()
        enabled: set[str] = set()
        if self.config.tools["n8n"].enabled and self.n8n.enabled:
            enabled.add("n8n")
        if self.config.tools["penpot"].enabled and self.penpot.enabled:
            enabled.add("penpot")
        if self.config.tools["appflowy"].enabled and self.appflowy.enabled:
            enabled.add("appflowy")
        if self.config.tools["plausible"].enabled and self.plausible.enabled:
            enabled.add("plausible")
        if self.config.tools["whisper"].enabled and self.whisper.enabled:
            enabled.add("whisper")
        if self.config.tools["ytdlp"].enabled and self.ytdlp.enabled:
            enabled.add("ytdlp")
        if self.config.tools["fooocus"].enabled and self.fooocus.enabled:
            enabled.add("fooocus")
        if self.config.tools["calcom"].enabled and self.calcom.enabled:
            enabled.add("calcom")
        return enabled

    def connector_status(self) -> dict[str, bool]:
        return {
            "n8n": self.config.tools["n8n"].enabled and self.n8n.enabled,
            "penpot": self.config.tools["penpot"].enabled and self.penpot.enabled,
            "appflowy": self.config.tools["appflowy"].enabled and self.appflowy.enabled,
            "plausible": self.config.tools["plausible"].enabled and self.plausible.enabled,
            "whisper": self.config.tools["whisper"].enabled and self.whisper.enabled,
            "ytdlp": self.config.tools["ytdlp"].enabled and self.ytdlp.enabled,
            "fooocus": self.config.tools["fooocus"].enabled and self.fooocus.enabled,
            "calcom": self.config.tools["calcom"].enabled and self.calcom.enabled,
        }

    async def call_tool(self, tool_name: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = params or {}
        tool = next((item for item in self._tools if item["name"] == tool_name), None)
        if tool is None:
            raise ValueError(f"Unknown MCP tool: {tool_name}")

        connector = tool.get("connector")
        if connector not in self._enabled_connectors():
            raise ValueError(f"Connector '{connector}' is disabled or not configured")

        if tool_name == "n8n_list_workflows":
            workflows = await self.n8n.list_workflows()
            return {"workflows": workflows}

        if tool_name == "n8n_trigger_workflow":
            result = await self.n8n.trigger_n8n_workflow(
                workflow_id=str(params["workflow_id"]),
                payload=params.get("payload"),
            )
            return {"result": result}

        if tool_name == "penpot_create_file":
            result = await self.penpot.create_file(
                project_id=str(params["project_id"]),
                name=str(params["name"]),
            )
            return {"result": result}

        if tool_name == "penpot_add_shape":
            result = await self.penpot.add_shape(
                file_id=str(params["file_id"]),
                shape_type=str(params["shape_type"]),
                position=dict(params["position"]),
                size=dict(params["size"]),
            )
            return {"result": result}

        if tool_name == "penpot_export_image":
            result = await self.penpot.export_image(
                file_id=str(params["file_id"]),
                format=str(params.get("format", "png")),
            )
            return {"result": result}

        if tool_name == "appflowy_create_page":
            result = await self.appflowy.create_page(
                view_id=str(params["view_id"]),
                title=str(params["title"]),
                content=str(params.get("content", "")),
            )
            return {"result": result}

        if tool_name == "appflowy_append_to_page":
            result = await self.appflowy.append_to_page(
                page_id=str(params["page_id"]),
                content=str(params["content"]),
            )
            return {"result": result}

        if tool_name == "appflowy_search_pages":
            result = await self.appflowy.search_pages(query=str(params["query"]))
            return {"result": result}

        if tool_name == "plausible_track_event":
            result = await self.plausible.track_event(
                event_name=str(params["event_name"]),
                props=params.get("props"),
            )
            return {"result": result}

        if tool_name == "plausible_get_stats":
            result = await self.plausible.get_stats(
                period=str(params.get("period", "7d")),
                metrics=params.get("metrics"),
            )
            return {"result": result}

        if tool_name == "whisper_transcribe":
            if params.get("audio_b64"):
                result = await self.whisper.transcribe_base64(
                    audio_b64=str(params["audio_b64"]),
                    language=params.get("language"),
                )
            else:
                source = params.get("audio_url") or params.get("audio_path")
                if not source:
                    raise ValueError("audio_url, audio_path, or audio_b64 is required")
                result = await self.whisper.transcribe_audio(
                    audio_path_or_url=str(source),
                    language=params.get("language"),
                )
            return {"result": result}

        if tool_name == "ytdlp_download_media":
            result = await self.ytdlp.download_media(
                url=str(params["url"]),
                format=params.get("format"),
                user_id=str(params.get("user_id", "default")),
            )
            return {"result": result}

        if tool_name == "ytdlp_extract_info":
            result = await self.ytdlp.extract_info(url=str(params["url"]))
            return {"result": result}

        if tool_name == "fooocus_generate_image":
            result = await self.fooocus.generate_image(
                prompt=str(params["prompt"]),
                negative_prompt=params.get("negative_prompt"),
                style=str(params.get("style", "")),
                aspect_ratio=str(params.get("aspect_ratio", "1024x1024")),
            )
            return {"result": result}

        if tool_name == "calcom_create_booking":
            result = await self.calcom.create_booking(
                event_type_id=params.get("event_type_id"),
                start_time=str(params["start_time"]),
                end_time=str(params["end_time"]),
                name=str(params["name"]),
                email=str(params["email"]),
                metadata=params.get("metadata"),
            )
            return {"result": result}

        if tool_name == "calcom_get_available_slots":
            result = await self.calcom.get_available_slots(
                event_type_id=params.get("event_type_id"),
                date=str(params["date"]),
            )
            return {"result": result}

        raise ValueError(f"Tool '{tool_name}' is not implemented")


def get_mcp_registry() -> MCPRegistry:
    global _registry
    if _registry is None:
        _registry = MCPRegistry()
    return _registry


def reset_mcp_registry() -> None:
    global _registry
    _registry = None
