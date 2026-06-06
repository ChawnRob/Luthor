from __future__ import annotations

import os
from datetime import date

from fastapi import APIRouter, Header, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from luthor.api.export_service import (
    ALLOWED_FORMATS,
    ALLOWED_TABLES,
    MEDIA_TYPES,
    LogExportService,
    get_export_token,
    verify_export_token,
)

router = APIRouter(tags=["export"])


@router.get("/export/logs")
def export_logs(
    request: Request,
    table: str = Query(default="inference_logs"),
    export_format: str = Query(default="csv", alias="format"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    x_export_token: str | None = Header(default=None, alias="X-Export-Token"),
):
    expected_token = get_export_token() or getattr(request.app.state, "export_token", None)
    if not verify_export_token(x_export_token, expected_token):
        raise HTTPException(status_code=401, detail="Invalid or missing export token")

    if table not in ALLOWED_TABLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid table. Allowed values: {', '.join(sorted(ALLOWED_TABLES))}",
        )

    if export_format not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Allowed values: {', '.join(sorted(ALLOWED_FORMATS))}",
        )

    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be before or equal to end_date")

    export_service: LogExportService = request.app.state.export_service

    try:
        file_path, filename = export_service.build_export_file(
            table,  # type: ignore[arg-type]
            export_format,  # type: ignore[arg-type]
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Export failed: {exc}") from exc

    def stream_file():
        try:
            with open(file_path, "rb") as handle:
                yield from handle
        finally:
            if os.path.exists(file_path):
                os.unlink(file_path)

    return StreamingResponse(
        stream_file(),
        media_type=MEDIA_TYPES[export_format],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
