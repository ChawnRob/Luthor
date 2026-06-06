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
