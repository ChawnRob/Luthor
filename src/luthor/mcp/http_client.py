from __future__ import annotations

from typing import Any

import httpx


class MCPHttpClient:
    """Shared async HTTP client for MCP tool connectors."""

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json,
            )
            response.raise_for_status()
            if not response.content:
                return {}
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                data = response.json()
                return data if isinstance(data, dict) else {"data": data}
            return {"text": response.text}
