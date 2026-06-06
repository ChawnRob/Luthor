from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from luthor.api.schemas import (
    AppFlowyToolRequest,
    AvailabilityResponse,
    BookingRequest,
    BookingResponse,
    DownloadRequest,
    DownloadResponse,
    GenerateImageRequest,
    GenerateImageResponse,
    N8nTriggerRequest,
    N8nTriggerResponse,
    N8nWorkflowsResponse,
    PenpotToolRequest,
    PlausibleToolRequest,
    ToolActionResponse,
    TranscribeRequest,
    TranscribeResponse,
)

router = APIRouter(tags=["tools"])


@router.get("/tools/n8n", response_model=N8nWorkflowsResponse)
async def list_n8n_workflows(request: Request) -> N8nWorkflowsResponse:
    registry = request.app.state.mcp_registry
    try:
        workflows = await registry.n8n.list_workflows()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"n8n request failed: {exc}") from exc
    return N8nWorkflowsResponse(workflows=workflows)


@router.post("/tools/n8n", response_model=N8nTriggerResponse)
async def trigger_n8n_workflow(
    payload: N8nTriggerRequest,
    request: Request,
) -> N8nTriggerResponse:
    registry = request.app.state.mcp_registry
    try:
        result = await registry.n8n.trigger_n8n_workflow(
            workflow_id=payload.workflow_id,
            payload=payload.payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"n8n trigger failed: {exc}") from exc
    return N8nTriggerResponse(result=result)


@router.post("/tools/penpot", response_model=ToolActionResponse)
async def penpot_tool_action(
    payload: PenpotToolRequest,
    request: Request,
) -> ToolActionResponse:
    registry = request.app.state.mcp_registry
    try:
        if payload.action == "create_file":
            if not payload.project_id or not payload.name:
                raise ValueError("project_id and name are required for create_file")
            result = await registry.penpot.create_file(payload.project_id, payload.name)
        elif payload.action == "add_shape":
            if not payload.file_id or not payload.shape_type:
                raise ValueError("file_id and shape_type are required for add_shape")
            result = await registry.penpot.add_shape(
                file_id=payload.file_id,
                shape_type=payload.shape_type,
                position=payload.position or {"x": 0, "y": 0},
                size=payload.size or {"width": 100, "height": 100},
            )
        elif payload.action == "export_image":
            if not payload.file_id:
                raise ValueError("file_id is required for export_image")
            result = await registry.penpot.export_image(payload.file_id, payload.format)
        else:
            raise ValueError(f"Unsupported PenPot action: {payload.action}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"PenPot request failed: {exc}") from exc
    return ToolActionResponse(result=result)


@router.post("/tools/appflowy", response_model=ToolActionResponse)
async def appflowy_tool_action(
    payload: AppFlowyToolRequest,
    request: Request,
) -> ToolActionResponse:
    registry = request.app.state.mcp_registry
    try:
        if payload.action == "create_page":
            if not payload.view_id or not payload.title:
                raise ValueError("view_id and title are required for create_page")
            result = await registry.appflowy.create_page(
                view_id=payload.view_id,
                title=payload.title,
                content=payload.content or "",
            )
        elif payload.action == "append_to_page":
            if not payload.page_id or payload.content is None:
                raise ValueError("page_id and content are required for append_to_page")
            result = await registry.appflowy.append_to_page(payload.page_id, payload.content)
        elif payload.action == "search_pages":
            if not payload.query:
                raise ValueError("query is required for search_pages")
            result = await registry.appflowy.search_pages(payload.query)
        else:
            raise ValueError(f"Unsupported AppFlowy action: {payload.action}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"AppFlowy request failed: {exc}") from exc
    return ToolActionResponse(result=result)


@router.post("/tools/plausible", response_model=ToolActionResponse)
async def plausible_tool_action(
    payload: PlausibleToolRequest,
    request: Request,
) -> ToolActionResponse:
    registry = request.app.state.mcp_registry
    try:
        if payload.action == "track_event":
            if not payload.event_name:
                raise ValueError("event_name is required for track_event")
            result = await registry.plausible.track_event(payload.event_name, payload.props)
        elif payload.action == "get_stats":
            result = await registry.plausible.get_stats(payload.period, payload.metrics)
        else:
            raise ValueError(f"Unsupported Plausible action: {payload.action}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Plausible request failed: {exc}") from exc
    return ToolActionResponse(result=result)


@router.post("/tools/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(payload: TranscribeRequest, request: Request) -> TranscribeResponse:
    registry = request.app.state.mcp_registry
    if not payload.audio_url and not payload.audio_b64:
        raise HTTPException(status_code=400, detail="audio_url or audio_b64 is required")
    try:
        if payload.audio_b64:
            result = await registry.whisper.transcribe_base64(
                audio_b64=payload.audio_b64,
                language=payload.language,
            )
        else:
            result = await registry.whisper.transcribe_audio(
                audio_path_or_url=payload.audio_url or "",
                language=payload.language,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Transcription failed: {exc}") from exc
    return TranscribeResponse(
        text=result["text"],
        language=result.get("language"),
        model=result["model"],
    )


@router.post("/tools/download", response_model=DownloadResponse)
async def download_media(payload: DownloadRequest, request: Request) -> DownloadResponse:
    registry = request.app.state.mcp_registry
    try:
        if payload.action == "extract_info":
            result = await registry.ytdlp.extract_info(payload.url)
        else:
            result = await registry.ytdlp.download_media(
                url=payload.url,
                format=payload.format,
                user_id=payload.user_id,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Download failed: {exc}") from exc
    return DownloadResponse(result=result)


@router.post("/tools/generate_image", response_model=GenerateImageResponse)
async def generate_image(payload: GenerateImageRequest, request: Request) -> GenerateImageResponse:
    registry = request.app.state.mcp_registry
    try:
        result = await registry.fooocus.generate_image(
            prompt=payload.prompt,
            negative_prompt=payload.negative_prompt,
            style=payload.style,
            aspect_ratio=payload.aspect_ratio,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Image generation failed: {exc}") from exc
    return GenerateImageResponse(
        image_url=result.get("image_url"),
        image_b64=result.get("image_b64"),
        prompt=result["prompt"],
        aspect_ratio=result["aspect_ratio"],
    )


@router.post("/tools/booking", response_model=BookingResponse)
async def create_booking(payload: BookingRequest, request: Request) -> BookingResponse:
    registry = request.app.state.mcp_registry
    try:
        result = await registry.calcom.create_booking(
            event_type_id=payload.event_type_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
            name=payload.name,
            email=payload.email,
            metadata=payload.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Booking failed: {exc}") from exc
    return BookingResponse(result=result)


@router.get("/tools/availability", response_model=AvailabilityResponse)
async def get_availability(
    request: Request,
    date: str,
    event_type_id: str | None = None,
) -> AvailabilityResponse:
    registry = request.app.state.mcp_registry
    try:
        result = await registry.calcom.get_available_slots(
            event_type_id=event_type_id,
            date=date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Availability lookup failed: {exc}") from exc
    return AvailabilityResponse(result=result)
