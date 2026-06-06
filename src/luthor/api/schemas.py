from typing import Any

from pydantic import BaseModel, Field


class EmbedRequest(BaseModel):
    observation: list[float] = Field(..., min_length=1, description="Raw observation vector")


class EmbedResponse(BaseModel):
    embedding_id: str
    embedding: list[float]
    latent_dim: int


class PredictRequest(BaseModel):
    observation: list[float] = Field(..., min_length=1)
    action: list[float] = Field(..., min_length=1)
    mc_samples: int | None = Field(default=None, ge=1, le=50)


class PredictResponse(BaseModel):
    predicted_latent: list[float]
    uncertainty: float
    latent_variance: list[float]


class ActiveLearnRequest(BaseModel):
    num_rounds: int | None = Field(default=None, ge=1, le=100)
    pool_size: int | None = Field(default=None, ge=1, le=512)
    query_batch_size: int | None = Field(default=None, ge=1, le=128)


class ActiveLearnRoundResponse(BaseModel):
    round_index: int
    mean_uncertainty: float
    mean_loss: float
    queried: int


class ActiveLearnResponse(BaseModel):
    rounds: list[ActiveLearnRoundResponse]
    final_mean_loss: float


class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    status: str
    postgres: str
    chromadb: str
    model_loaded: bool


class ErrorResponse(BaseModel):
    detail: str
    metadata: dict[str, Any] | None = None


class PromptVersionResponse(BaseModel):
    name: str
    version: str
    content: str


class PromptListResponse(BaseModel):
    prompts: list[PromptVersionResponse]


class ABVersionMetrics(BaseModel):
    calls: int
    mean_uncertainty: float | None = None
    mean_loss: float | None = None
    success_rate: float | None = None


class ABMetricsResponse(BaseModel):
    window_hours: int
    versions: dict[str, ABVersionMetrics]
    winner: str | None = None


class LabelRequest(BaseModel):
    sample_id: str
    correct_outcome: dict[str, Any]


class LabelResponse(BaseModel):
    sample_id: str
    stored: bool


class PendingLabelItem(BaseModel):
    sample_id: str
    observation: list[float]
    action: list[float]
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: float


class PendingLabelsResponse(BaseModel):
    pending: list[PendingLabelItem]


class MCPToolInfo(BaseModel):
    name: str
    type: str
    connector: str
    description: str
    endpoint: str


class MCPToolsResponse(BaseModel):
    enabled: bool
    connectors: dict[str, bool]
    tools: list[MCPToolInfo]


class N8nTriggerRequest(BaseModel):
    workflow_id: str
    payload: dict[str, Any] = Field(default_factory=dict)


class N8nWorkflowsResponse(BaseModel):
    workflows: list[dict[str, Any]]


class N8nTriggerResponse(BaseModel):
    result: dict[str, Any]


class PenpotToolRequest(BaseModel):
    action: str = Field(..., description="create_file | add_shape | export_image")
    project_id: str | None = None
    name: str | None = None
    file_id: str | None = None
    shape_type: str | None = None
    position: dict[str, float] | None = None
    size: dict[str, float] | None = None
    format: str = "png"


class AppFlowyToolRequest(BaseModel):
    action: str = Field(..., description="create_page | append_to_page | search_pages")
    view_id: str | None = None
    title: str | None = None
    content: str | None = None
    page_id: str | None = None
    query: str | None = None


class PlausibleToolRequest(BaseModel):
    action: str = Field(..., description="track_event | get_stats")
    event_name: str | None = None
    props: dict[str, Any] = Field(default_factory=dict)
    period: str = "7d"
    metrics: list[str] | None = None


class ToolActionResponse(BaseModel):
    result: dict[str, Any]


class MCPOrchestrateRequest(BaseModel):
    message: str = Field(..., min_length=1)
    system_prompt: str | None = None


class MCPOrchestrateResponse(BaseModel):
    message: str
    used_tools: bool
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)


class TranscribeRequest(BaseModel):
    audio_url: str | None = None
    audio_b64: str | None = None
    language: str | None = None


class TranscribeResponse(BaseModel):
    text: str
    language: str | None = None
    model: str


class DownloadRequest(BaseModel):
    url: str
    format: str = "best"
    user_id: str = "default"
    action: str = Field(default="download", description="download | extract_info")


class DownloadResponse(BaseModel):
    result: dict[str, Any]


class GenerateImageRequest(BaseModel):
    prompt: str
    negative_prompt: str | None = None
    style: str = ""
    aspect_ratio: str = "1024x1024"


class GenerateImageResponse(BaseModel):
    image_url: str | None = None
    image_b64: str | None = None
    prompt: str
    aspect_ratio: str


class BookingRequest(BaseModel):
    event_type_id: str | None = None
    start_time: str
    end_time: str
    name: str
    email: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class BookingResponse(BaseModel):
    result: dict[str, Any]


class AvailabilityResponse(BaseModel):
    result: dict[str, Any]


class DemoFullRequest(BaseModel):
    model_config = {"populate_by_name": True}

    message: str = Field(..., min_length=1)
    async_mode: bool = Field(default=False, alias="async")


class DemoFullResponse(BaseModel):
    task_id: str | None = None
    status: str
    warnings: list[str] = Field(default_factory=list)
    summary: dict[str, Any] | None = None


class DemoTaskResponse(BaseModel):
    task_id: str
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None


class InferenceLogItem(BaseModel):
    id: int
    endpoint: str | None = None
    request_payload: dict[str, Any] | None = None
    response_payload: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    model_version: str | None = None
    created_at: str | None = None


class InferenceLogsResponse(BaseModel):
    items: list[InferenceLogItem]
    total: int
    page: int
    page_size: int


class ConfigConnectorItem(BaseModel):
    enabled: bool
    url: str = ""
    api_key_set: bool = False
    token_set: bool = False
    site_id: str = ""
    model: str | None = None
    device: str | None = None


class ConfigResponse(BaseModel):
    mcp_enabled: bool
    mcp_model: str
    mcp_llm_provider: str
    postgres_configured: bool
    chroma_host: str
    chroma_port: int
    connectors: dict[str, ConfigConnectorItem]
    message: str = (
        "Configuration is read-only. Set environment variables in .env or .env.prod on the server."
    )


class AuthSignupRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1)


class AuthSigninRequest(BaseModel):
    email: str
    password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int | None = None
    user_id: str | None = None


class AuthOAuthResponse(BaseModel):
    provider: str
    authorization_url: str


class AuthMfaEnableRequest(BaseModel):
    access_token: str = Field(..., min_length=10)


class AuthMfaEnableResponse(BaseModel):
    factor_id: str | None = None
    totp_uri: str | None = None
    qr_code: str | None = None
    secret: str | None = None


class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str | None = None
    quota_tier: str
    subscription_status: str
    mfa_enabled: bool
    usage: dict[str, int | str]


class ToolSyncItem(BaseModel):
    connector: str
    enabled: bool
    status: str
    last_sync_at: str | None = None
    tools_count: int = 0


class ToolSyncResponse(BaseModel):
    connectors: list[ToolSyncItem]
    synced_at: str
