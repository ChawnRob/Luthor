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
