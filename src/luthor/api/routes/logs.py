from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, Query, Request

from luthor.api.schemas import InferenceLogItem, InferenceLogsResponse
from luthor.api.storage import EXPORT_TABLES, InferenceLogStore

router = APIRouter(tags=["logs"])


def _serialize_log_row(row: dict) -> InferenceLogItem:
    created_at = row.get("created_at")
    created_str = created_at.isoformat() if hasattr(created_at, "isoformat") else (
        str(created_at) if created_at is not None else None
    )
    return InferenceLogItem(
        id=int(row["id"]),
        endpoint=row.get("endpoint"),
        request_payload=row.get("request_payload"),
        response_payload=row.get("response_payload"),
        metadata=row.get("metadata"),
        model_version=row.get("model_version"),
        created_at=created_str,
    )


@router.get("/logs", response_model=InferenceLogsResponse)
def list_inference_logs(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    endpoint: str | None = Query(default=None),
    model_version: str | None = Query(default=None),
    table: str = Query(default="inference_logs"),
) -> InferenceLogsResponse:
    if table not in EXPORT_TABLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid table. Allowed values: {', '.join(sorted(EXPORT_TABLES))}",
        )

    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be before or equal to end_date")

    log_store: InferenceLogStore = request.app.state.log_store

    try:
        rows, total = log_store.list_inference_logs(
            page=page,
            page_size=page_size,
            start_date=start_date,
            end_date=end_date,
            endpoint=endpoint,
            model_version=model_version,
            table=table,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Failed to fetch logs: {exc}") from exc

    return InferenceLogsResponse(
        items=[_serialize_log_row(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )
