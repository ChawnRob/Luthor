from __future__ import annotations

import os
from typing import Any

from luthor.mcp.http_client import MCPHttpClient


class CalComConnector:
    """Booking and availability via Cal.com API."""

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        event_type_id: str | None = None,
        http_client: MCPHttpClient | None = None,
    ):
        self.api_url = (api_url or os.getenv("CALCOM_API_URL", "http://localhost:3000")).rstrip("/")
        self.api_key = api_key or os.getenv("CALCOM_API_KEY", "")
        self.event_type_id = event_type_id or os.getenv("CALCOM_EVENT_TYPE_ID", "")
        self.http = http_client or MCPHttpClient()

    @property
    def enabled(self) -> bool:
        return bool(self.api_url and self.api_key)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _require_config(self) -> None:
        if not self.enabled:
            raise ValueError(
                "Cal.com is not configured (set CALCOM_API_URL and CALCOM_API_KEY)"
            )

    async def create_booking(
        self,
        event_type_id: str | None,
        start_time: str,
        end_time: str,
        name: str,
        email: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._require_config()
        resolved_event_type = event_type_id or self.event_type_id
        if not resolved_event_type:
            raise ValueError("event_type_id is required")

        payload = {
            "eventTypeId": int(resolved_event_type)
            if str(resolved_event_type).isdigit()
            else resolved_event_type,
            "start": start_time,
            "end": end_time,
            "responses": {
                "name": name,
                "email": email,
            },
            "metadata": metadata or {},
            "status": "PENDING",
        }
        result = await self.http.request(
            "POST",
            f"{self.api_url}/api/bookings",
            headers=self._headers(),
            json=payload,
        )
        return {
            "booking": result,
            "status": result.get("status", "PENDING"),
            "confirmation": result.get("uid") or result.get("id"),
        }

    async def get_available_slots(
        self,
        event_type_id: str | None,
        date: str,
    ) -> dict[str, Any]:
        self._require_config()
        resolved_event_type = event_type_id or self.event_type_id
        if not resolved_event_type:
            raise ValueError("event_type_id is required")

        result = await self.http.request(
            "GET",
            f"{self.api_url}/api/slots",
            headers=self._headers(),
            params={
                "eventTypeId": resolved_event_type,
                "startTime": date,
                "endTime": date,
            },
        )
        slots = result.get("slots") or result.get("data") or result
        return {"date": date, "event_type_id": resolved_event_type, "slots": slots}
