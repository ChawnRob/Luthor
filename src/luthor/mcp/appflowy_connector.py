from __future__ import annotations

import os
from typing import Any

from luthor.mcp.http_client import MCPHttpClient


class AppFlowyConnector:
    """Connector for AppFlowy workspace memory."""

    def __init__(
        self,
        api_url: str | None = None,
        token: str | None = None,
        http_client: MCPHttpClient | None = None,
    ):
        self.api_url = (api_url or os.getenv("APPFLOWY_API_URL", "")).rstrip("/")
        self.token = token or os.getenv("APPFLOWY_TOKEN", "")
        self.http = http_client or MCPHttpClient()

    @property
    def enabled(self) -> bool:
        return bool(self.api_url and self.token)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _require_config(self) -> None:
        if not self.enabled:
            raise ValueError("AppFlowy is not configured (set APPFLOWY_API_URL and APPFLOWY_TOKEN)")

    async def create_page(
        self,
        view_id: str,
        title: str,
        content: str = "",
    ) -> dict[str, Any]:
        self._require_config()
        return await self.http.request(
            "POST",
            f"{self.api_url}/api/pages",
            headers=self._headers(),
            json={"view_id": view_id, "title": title, "content": content},
        )

    async def append_to_page(self, page_id: str, content: str) -> dict[str, Any]:
        self._require_config()
        return await self.http.request(
            "POST",
            f"{self.api_url}/api/pages/{page_id}/append",
            headers=self._headers(),
            json={"content": content},
        )

    async def search_pages(self, query: str) -> dict[str, Any]:
        self._require_config()
        return await self.http.request(
            "GET",
            f"{self.api_url}/api/pages/search",
            headers=self._headers(),
            params={"q": query},
        )
