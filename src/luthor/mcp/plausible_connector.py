from __future__ import annotations

import os
from typing import Any

from luthor.mcp.http_client import MCPHttpClient


class PlausibleConnector:
    """Connector for Plausible Analytics."""

    def __init__(
        self,
        api_url: str | None = None,
        site_id: str | None = None,
        token: str | None = None,
        http_client: MCPHttpClient | None = None,
    ):
        self.api_url = (api_url or os.getenv("PLAUSIBLE_API_URL", "https://plausible.io")).rstrip("/")
        self.site_id = site_id or os.getenv("PLAUSIBLE_SITE_ID", "")
        self.token = token or os.getenv("PLAUSIBLE_TOKEN", "")
        self.http = http_client or MCPHttpClient()

    @property
    def enabled(self) -> bool:
        return bool(self.api_url and self.site_id and self.token)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _require_config(self) -> None:
        if not self.enabled:
            raise ValueError(
                "Plausible is not configured (set PLAUSIBLE_API_URL, PLAUSIBLE_SITE_ID, PLAUSIBLE_TOKEN)"
            )

    async def track_event(
        self,
        event_name: str,
        props: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._require_config()
        return await self.http.request(
            "POST",
            f"{self.api_url}/api/v2/events",
            headers=self._headers(),
            json={
                "name": event_name,
                "domain": self.site_id,
                "props": props or {},
            },
        )

    async def get_stats(
        self,
        period: str = "7d",
        metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        self._require_config()
        metric_list = metrics or ["visitors", "pageviews", "bounce_rate"]
        return await self.http.request(
            "GET",
            f"{self.api_url}/api/v2/stats/aggregate",
            headers=self._headers(),
            params={
                "site_id": self.site_id,
                "period": period,
                "metrics": ",".join(metric_list),
            },
        )
