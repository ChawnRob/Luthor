from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse

from luthor.active_learning.pending_labels import get_pending_label_registry
from luthor.api.metrics import (
    PrometheusMiddleware,
    metrics_response,
    record_active_learning_round,
    record_jepa_inference_latency,
    record_model_version_request,
    start_push_gateway_if_configured,
    stop_push_gateway,
)
from luthor.api.export_service import LogExportService, get_export_token
from luthor.api.routes import (
    ab_router,
    export_router,
    label_router,
    mcp_router,
    prompts_router,
    tools_router,
)
from luthor.mcp.registry import get_mcp_registry, reset_mcp_registry
from luthor.orchestrator import MCPOrchestrator
from luthor.api.schemas import (
    ActiveLearnRequest,
    ActiveLearnResponse,
    ActiveLearnRoundResponse,
    EmbedRequest,
    EmbedResponse,
    HealthResponse,
    PredictRequest,
    PredictResponse,
)
from luthor.api.services import JEPAService
from luthor.api.storage import EmbeddingStore, InferenceLogStore
from luthor.config import get_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.config = get_config()
    app.state.jepa_service = JEPAService(app.state.config)
    app.state.log_store = InferenceLogStore()
    app.state.embedding_store = EmbeddingStore()
    app.state.export_service = LogExportService(app.state.log_store)
    app.state.export_token = get_export_token()
    app.state.pending_registry = get_pending_label_registry()
    app.state.mcp_registry = get_mcp_registry()
    app.state.orchestrator = MCPOrchestrator(registry=app.state.mcp_registry)
    start_push_gateway_if_configured()
    yield
    stop_push_gateway()
    reset_mcp_registry()


def create_app() -> FastAPI:
    application = FastAPI(
        title="Luthor JEPA API",
        description="FastAPI wrapper for JEPA SLM embedding, prediction, and active learning.",
        version="1.0.0",
        lifespan=lifespan,
    )

    application.add_middleware(PrometheusMiddleware)
    application.include_router(export_router)
    application.include_router(prompts_router)
    application.include_router(ab_router)
    application.include_router(label_router)
    application.include_router(mcp_router)
    application.include_router(tools_router)

    @application.get("/metrics", include_in_schema=False)
    def metrics():
        return metrics_response()

    label_ui_path = Path(__file__).resolve().parents[3] / "web" / "label_ui.html"

    @application.get("/label-ui")
    def label_ui() -> FileResponse:
        if not label_ui_path.exists():
            raise HTTPException(status_code=404, detail="label_ui.html not found")
        return FileResponse(label_ui_path)

    @application.get("/health", response_model=HealthResponse)
    def health(request: Request) -> HealthResponse:
        postgres_status = "ok"
        chroma_status = "ok"

        try:
            request.app.state.log_store.ping()
        except Exception as exc:  # pragma: no cover - depends on docker services
            postgres_status = f"error: {exc}"

        try:
            request.app.state.embedding_store.ping()
        except Exception as exc:  # pragma: no cover - depends on docker services
            chroma_status = f"error: {exc}"

        overall = "ok" if postgres_status == "ok" and chroma_status == "ok" else "degraded"
        return HealthResponse(
            status=overall,
            postgres=postgres_status,
            chromadb=chroma_status,
            model_loaded=request.app.state.jepa_service is not None,
        )

    @application.post("/embed", response_model=EmbedResponse)
    def embed(
        payload: EmbedRequest,
        request: Request,
        x_model_version: str | None = Header(default=None, alias="X-Model-Version"),
    ) -> EmbedResponse:
        service: JEPAService = request.app.state.jepa_service
        log_store: InferenceLogStore = request.app.state.log_store
        embedding_store: EmbeddingStore = request.app.state.embedding_store

        try:
            started = time.perf_counter()
            embedding_id, embedding, model_version = service.embed(
                payload.observation,
                model_version=x_model_version,
            )
            record_jepa_inference_latency("/embed", time.perf_counter() - started)
            record_model_version_request("/embed", model_version)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        response = EmbedResponse(
            embedding_id=embedding_id,
            embedding=embedding,
            latent_dim=len(embedding),
        )

        try:
            embedding_store.add_embedding(
                embedding_id,
                embedding,
                metadata={"observation": payload.observation},
            )
            log_store.log_inference(
                endpoint="/embed",
                request_payload=payload.model_dump(),
                response_payload=response.model_dump(),
                metadata={"embedding_id": embedding_id},
                model_version=model_version,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Storage unavailable: {exc}",
            ) from exc

        return response

    @application.post("/predict", response_model=PredictResponse)
    def predict(
        payload: PredictRequest,
        request: Request,
        x_model_version: str | None = Header(default=None, alias="X-Model-Version"),
    ) -> PredictResponse:
        service: JEPAService = request.app.state.jepa_service
        log_store: InferenceLogStore = request.app.state.log_store

        try:
            started = time.perf_counter()
            result = service.predict(
                payload.observation,
                payload.action,
                payload.mc_samples,
                model_version=x_model_version,
            )
            record_jepa_inference_latency("/predict", time.perf_counter() - started)
            record_model_version_request("/predict", str(result["model_version"]))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        response = PredictResponse(
            predicted_latent=result["predicted_latent"],  # type: ignore[arg-type]
            uncertainty=result["uncertainty"],  # type: ignore[arg-type]
            latent_variance=result["latent_variance"],  # type: ignore[arg-type]
        )

        try:
            log_store.log_inference(
                endpoint="/predict",
                request_payload=payload.model_dump(),
                response_payload=response.model_dump(),
                metadata={"uncertainty": response.uncertainty},
                model_version=str(result["model_version"]),
            )
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Storage unavailable: {exc}",
            ) from exc

        return response

    @application.post("/active_learn", response_model=ActiveLearnResponse)
    def active_learn(payload: ActiveLearnRequest, request: Request) -> ActiveLearnResponse:
        service: JEPAService = request.app.state.jepa_service
        log_store: InferenceLogStore = request.app.state.log_store

        try:
            results = service.active_learn(
                num_rounds=payload.num_rounds,
                pool_size=payload.pool_size,
                query_batch_size=payload.query_batch_size,
            )
            for _ in results:
                record_active_learning_round()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        rounds = [
            ActiveLearnRoundResponse(
                round_index=result.round_index,
                mean_uncertainty=result.mean_uncertainty,
                mean_loss=result.mean_loss,
                queried=result.queried,
            )
            for result in results
        ]
        final_mean_loss = rounds[-1].mean_loss if rounds else 0.0
        response = ActiveLearnResponse(rounds=rounds, final_mean_loss=final_mean_loss)

        try:
            for result in results:
                log_store.log_active_learning_round(
                    round_index=result.round_index,
                    mean_uncertainty=result.mean_uncertainty,
                    mean_loss=result.mean_loss,
                    queried=result.queried,
                    metadata=payload.model_dump(),
                )
            log_store.log_inference(
                endpoint="/active_learn",
                request_payload=payload.model_dump(),
                response_payload=response.model_dump(),
            )
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Storage unavailable: {exc}",
            ) from exc

        return response

    return application


app = create_app()
