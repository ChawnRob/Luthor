from __future__ import annotations

import time
from typing import Any

import httpx

DEFAULT_API_URL = "https://api.open-meteo.com/v1/forecast"
CACHE_TTL_SECONDS = 300
_cache: dict[tuple[float, float], dict[str, Any]] = {}


def get_weather(
    latitude: float,
    longitude: float,
    *,
    api_url: str = DEFAULT_API_URL,
    cache_ttl: int = CACHE_TTL_SECONDS,
) -> dict[str, Any]:
    """Fetch current weather from Open-Meteo with a simple in-memory cache."""
    cache_key = (round(latitude, 2), round(longitude, 2))
    now = time.time()

    cached = _cache.get(cache_key)
    if cached is not None and now - cached["fetched_at"] < cache_ttl:
        return cached["data"]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m,weather_code",
    }
    with httpx.Client(timeout=10.0) as client:
        response = client.get(api_url, params=params)
        response.raise_for_status()
        payload = response.json()

    current = payload.get("current", {})
    data = {
        "latitude": latitude,
        "longitude": longitude,
        "temperature_c": current.get("temperature_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "weather_code": current.get("weather_code"),
        "source": "open-meteo",
    }
    _cache[cache_key] = {"fetched_at": now, "data": data}
    return data


def clear_weather_cache() -> None:
    _cache.clear()
