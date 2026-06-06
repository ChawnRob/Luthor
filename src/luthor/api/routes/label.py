from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from luthor.api.schemas import LabelRequest, LabelResponse, PendingLabelsResponse

router = APIRouter(tags=["labels"])


@router.get("/label/pending", response_model=PendingLabelsResponse)
def list_pending_labels(request: Request) -> PendingLabelsResponse:
    registry = request.app.state.pending_registry
    return PendingLabelsResponse(pending=registry.list_pending())


@router.post("/label", response_model=LabelResponse)
def submit_label(payload: LabelRequest, request: Request) -> LabelResponse:
    registry = request.app.state.pending_registry

    if not registry.submit_label(payload.sample_id, payload.correct_outcome):
        raise HTTPException(
            status_code=404,
            detail=f"No pending sample with sample_id={payload.sample_id}",
        )

    label_store = getattr(request.app.state, "label_store", None)
    if label_store is not None:
        try:
            label_store.save_label(payload.sample_id, payload.correct_outcome)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to persist label: {exc}",
            ) from exc

    return LabelResponse(sample_id=payload.sample_id, stored=True)
