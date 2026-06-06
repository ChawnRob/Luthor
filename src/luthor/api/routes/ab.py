from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from luthor.api.ab_metrics import compare_ab_metrics
from luthor.api.schemas import ABMetricsResponse

router = APIRouter(tags=["ab-testing"])


@router.get("/ab/metrics", response_model=ABMetricsResponse)
def ab_metrics(request: Request, window_hours: int = 24) -> ABMetricsResponse:
    if not request.app.state.config.ab_testing.enabled:
        raise HTTPException(status_code=403, detail="A/B testing is disabled")

    try:
        payload = compare_ab_metrics(
            request.app.state.log_store,
            window_hours=window_hours,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Failed to compute A/B metrics: {exc}") from exc

    return ABMetricsResponse(**payload)
