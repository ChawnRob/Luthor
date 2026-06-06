from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from luthor.api.schemas import WeatherResponse
from luthor.tools.weather_tool import get_weather

router = APIRouter(tags=["tools"])


@router.get("/tools/weather", response_model=WeatherResponse)
def weather(
    request: Request,
    latitude: float,
    longitude: float,
) -> WeatherResponse:
    weather_cfg = request.app.state.config.tools.weather
    if not weather_cfg.enabled:
        raise HTTPException(status_code=403, detail="Weather tool is disabled")

    try:
        data = get_weather(latitude, longitude, api_url=weather_cfg.api_url)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Weather API error: {exc}") from exc

    return WeatherResponse(**data)
