from __future__ import annotations

import asyncio
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from luthor.api.schemas import DemoFullRequest, DemoFullResponse, DemoTaskResponse
from luthor.demo_workflow import (
    check_mcp_availability,
    get_demo_task,
    register_demo_task,
    run_demo_task_background,
    run_demo_workflow,
)

router = APIRouter(tags=["demo"])

DEMO_TIMEOUT_SECONDS = 300


@router.post("/demo/full", response_model=DemoFullResponse)
async def run_full_demo(
    payload: DemoFullRequest,
    request: Request,
    background_tasks: BackgroundTasks,
) -> DemoFullResponse:
    registry = request.app.state.mcp_registry
    orchestrator = request.app.state.orchestrator

    ok, error_message, warnings = check_mcp_availability(registry)
    if not ok:
        raise HTTPException(status_code=400, detail=error_message)

    if payload.async_mode:
        task_id = uuid.uuid4().hex
        register_demo_task(task_id, payload.message)
        background_tasks.add_task(
            run_demo_task_background,
            task_id,
            payload.message,
            orchestrator=orchestrator,
            registry=registry,
        )
        return DemoFullResponse(
            task_id=task_id,
            status="pending",
            warnings=warnings,
        )

    try:
        summary = await asyncio.wait_for(
            run_demo_workflow(
                payload.message,
                orchestrator=orchestrator,
                registry=registry,
            ),
            timeout=DEMO_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail=f"Demo workflow exceeded {DEMO_TIMEOUT_SECONDS}s timeout",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Demo workflow failed: {exc}") from exc

    return DemoFullResponse(
        status="completed",
        warnings=warnings,
        summary=summary.to_dict(),
    )


@router.get("/demo/tasks/{task_id}", response_model=DemoTaskResponse)
def get_demo_task_status(task_id: str) -> DemoTaskResponse:
    task = get_demo_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Unknown task_id={task_id}")
    return DemoTaskResponse(
        task_id=task_id,
        status=task["status"],
        result=task.get("result"),
        error=task.get("error"),
    )
