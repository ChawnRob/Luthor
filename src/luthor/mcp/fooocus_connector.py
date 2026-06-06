from __future__ import annotations

import os
from typing import Any

from luthor.mcp.http_client import MCPHttpClient


class FooocusConnector:
    """Image generation via a Fooocus REST API."""

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        http_client: MCPHttpClient | None = None,
    ):
        self.api_url = (api_url or os.getenv("FOOOCUS_API_URL", "http://localhost:8888")).rstrip("/")
        self.api_key = api_key or os.getenv("FOOOCUS_API_KEY", "")
        self.http = http_client or MCPHttpClient(timeout=120.0)

    @property
    def enabled(self) -> bool:
        return bool(self.api_url)

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def _health_check(self) -> None:
        try:
            await self.http.request(
                "GET",
                f"{self.api_url}/health",
                headers=self._headers(),
            )
        except Exception as exc:
            raise RuntimeError(
                f"Fooocus unavailable at {self.api_url}. Start the Fooocus API server first."
            ) from exc

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str | None = None,
        style: str = "",
        aspect_ratio: str = "1024x1024",
    ) -> dict[str, Any]:
        if not self.enabled:
            raise ValueError("Fooocus is not configured (set FOOOCUS_API_URL)")

        await self._health_check()
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "style": style,
            "aspect_ratio": aspect_ratio,
        }
        result = await self.http.request(
            "POST",
            f"{self.api_url}/v1/generation/text-to-image",
            headers=self._headers(),
            json=payload,
        )
        image_url = result.get("image_url") or result.get("url")
        image_b64 = result.get("image_b64") or result.get("b64")
        if not image_url and not image_b64:
            raise RuntimeError("Fooocus returned no image payload")
        return {
            "image_url": image_url,
            "image_b64": image_b64,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
        }
