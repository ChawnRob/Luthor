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


class LabelRequest(BaseModel):
    sample_id: str
    correct_outcome: dict[str, Any]


class LabelResponse(BaseModel):
    sample_id: str
    stored: bool


class PendingLabelItem(BaseModel):
    sample_id: str
    observation: list[float]
    action: Any
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: float


class PendingLabelsResponse(BaseModel):
    pending: list[PendingLabelItem]


class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    temperature_c: float | None = None
    wind_speed_kmh: float | None = None
    weather_code: int | None = None
    source: str
