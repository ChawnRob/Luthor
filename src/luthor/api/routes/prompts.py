from __future__ import annotations

from fastapi import APIRouter

from luthor.api.schemas import PromptListResponse, PromptVersionResponse
from luthor.prompts.loader import list_prompts

router = APIRouter(tags=["prompts"])


@router.get("/prompts", response_model=PromptListResponse)
def get_prompts() -> PromptListResponse:
    prompts = [
        PromptVersionResponse(name=item["name"], version=item["version"], content=item["content"])
        for item in list_prompts()
    ]
    return PromptListResponse(prompts=prompts)
