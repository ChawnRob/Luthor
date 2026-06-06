from __future__ import annotations

import os

from fastapi import APIRouter, Request

from luthor.api.schemas import ConfigConnectorItem, ConfigResponse
from luthor.config import LuthorConfig

router = APIRouter(tags=["config"])


def _secret_set(value: str | None) -> bool:
    return bool(value and value.strip())


@router.get("/config", response_model=ConfigResponse)
def read_config(request: Request) -> ConfigResponse:
    config: LuthorConfig = request.app.state.config
    connectors: dict[str, ConfigConnectorItem] = {}

    for name, connector in config.mcp.tools.items():
        connectors[name] = ConfigConnectorItem(
            enabled=connector.enabled,
            url=connector.url,
            api_key_set=_secret_set(connector.api_key),
            token_set=_secret_set(connector.token),
            site_id=connector.site_id,
            model=connector.model if name == "whisper" else None,
            device=connector.device if name == "whisper" else None,
        )

    postgres_url = os.getenv("LUTHOR_POSTGRES_URL", "")
    chroma_host = os.getenv("LUTHOR_CHROMA_HOST", "localhost")
    chroma_port = int(os.getenv("LUTHOR_CHROMA_PORT", "8001"))

    return ConfigResponse(
        mcp_enabled=config.mcp.enabled,
        mcp_model=os.getenv("LUTHOR_MCP_MODEL", "mistral-small-latest"),
        mcp_llm_provider=os.getenv("LUTHOR_MCP_LLM_PROVIDER", "mistral"),
        postgres_configured=_secret_set(postgres_url),
        chroma_host=chroma_host,
        chroma_port=chroma_port,
        connectors=connectors,
    )
