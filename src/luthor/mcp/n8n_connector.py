from __future__ import annotations

import os
from typing import Any

from luthor.mcp.http_client import MCPHttpClient


class N8nConnector:
    """Connector for n8n workflow automation."""

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        http_client: MCPHttpClient | None = None,
    ):
        self.api_url = (api_url or os.getenv("N8N_API_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("N8N_API_KEY", "")
        self.http = http_client or MCPHttpClient()

    @property
    def enabled(self) -> bool:
        return bool(self.api_url and self.api_key)

    def _headers(self) -> dict[str, str]:
        return {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

    def _require_config(self) -> None:
        if not self.enabled:
            raise ValueError("n8n is not configured (set N8N_API_URL and N8N_API_KEY)")

    async def list_workflows(self) -> list[dict[str, Any]]:
        self._require_config()
        payload = await self.http.request(
            "GET",
            f"{self.api_url}/api/v1/workflows",
            headers=self._headers(),
        )
        data = payload.get("data", payload)
        if isinstance(data, list):
            return data
        return [data] if data else []

    async def trigger_n8n_workflow(
        self,
        workflow_id: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Trigger a workflow via the execute API or webhook fallback."""
        self._require_config()
        body = payload or {}
        try:
            return await self.http.request(
                "POST",
                f"{self.api_url}/api/v1/workflows/{workflow_id}/execute",
                headers=self._headers(),
                json=body,
            )
        except Exception:
            return await self.http.request(
                "POST",
                f"{self.api_url}/webhook/{workflow_id}",
                headers={"Content-Type": "application/json"},
                json=body,
            )
