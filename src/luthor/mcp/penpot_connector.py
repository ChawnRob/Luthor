from __future__ import annotations

import os
from typing import Any

from luthor.mcp.http_client import MCPHttpClient


class PenpotConnector:
    """Connector for PenPot design operations."""

    def __init__(
        self,
        api_url: str | None = None,
        access_token: str | None = None,
        http_client: MCPHttpClient | None = None,
    ):
        self.api_url = (api_url or os.getenv("PENPOT_API_URL", "")).rstrip("/")
        self.access_token = access_token or os.getenv("PENPOT_ACCESS_TOKEN", "")
        self.http = http_client or MCPHttpClient()

    @property
    def enabled(self) -> bool:
        return bool(self.api_url and self.access_token)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _require_config(self) -> None:
        if not self.enabled:
            raise ValueError("PenPot is not configured (set PENPOT_API_URL and PENPOT_ACCESS_TOKEN)")

    async def create_file(self, project_id: str, name: str) -> dict[str, Any]:
        self._require_config()
        return await self.http.request(
            "POST",
            f"{self.api_url}/api/rpc/command/create-file",
            headers=self._headers(),
            json={"project-id": project_id, "name": name},
        )

    async def add_shape(
        self,
        file_id: str,
        shape_type: str,
        position: dict[str, float],
        size: dict[str, float],
    ) -> dict[str, Any]:
        self._require_config()
        return await self.http.request(
            "POST",
            f"{self.api_url}/api/rpc/command/create-shape",
            headers=self._headers(),
            json={
                "file-id": file_id,
                "type": shape_type,
                "x": position.get("x", 0),
                "y": position.get("y", 0),
                "width": size.get("width", 100),
                "height": size.get("height", 100),
            },
        )

    async def export_image(self, file_id: str, format: str = "png") -> dict[str, Any]:
        self._require_config()
        return await self.http.request(
            "GET",
            f"{self.api_url}/api/export",
            headers=self._headers(),
            params={"file-id": file_id, "format": format},
        )
