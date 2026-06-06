from __future__ import annotations

import os
import re
import threading
import time
from typing import Callable

from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest, push_to_gateway
from prometheus_client import REGISTRY
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests processed by the API",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

JEPA_INFERENCE_LATENCY = Histogram(
    "jepa_inference_latency",
    "JEPA embed/predict inference latency in seconds",
    ["endpoint"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
)

ACTIVE_LEARNING_ROUNDS_TOTAL = Counter(
    "active_learning_rounds_total",
    "Total active-learning rounds completed",
)

MODEL_VERSION_REQUESTS_TOTAL = Counter(
    "model_version_requests_total",
    "Inference requests grouped by model version",
    ["endpoint", "model_version"],
)

_PUSH_INTERVAL_SECONDS = 15
_push_stop = threading.Event()
_push_thread: threading.Thread | None = None


def metrics_response() -> Response:
    payload = generate_latest(REGISTRY)
    return Response(content=payload, media_type=CONTENT_TYPE_LATEST)


def record_jepa_inference_latency(endpoint: str, duration_seconds: float) -> None:
    JEPA_INFERENCE_LATENCY.labels(endpoint=endpoint).observe(duration_seconds)


def record_active_learning_round() -> None:
    ACTIVE_LEARNING_ROUNDS_TOTAL.inc()


def record_model_version_request(endpoint: str, model_version: str) -> None:
    MODEL_VERSION_REQUESTS_TOTAL.labels(
        endpoint=endpoint,
        model_version=model_version or "default",
    ).inc()


def parse_counter_total(metrics_text: str, metric_name: str, label_fragment: str = "") -> float:
    """Parse a Prometheus counter value from exposition text."""
    labeled = re.compile(
        rf"^{re.escape(metric_name)}\{{[^}}]*{re.escape(label_fragment)}[^}}]*\}}\s+([0-9.eE+-]+)$",
        re.MULTILINE,
    )
    unlabeled = re.compile(
        rf"^{re.escape(metric_name)}\s+([0-9.eE+-]+)$",
        re.MULTILINE,
    )
    total = 0.0
    for match in labeled.finditer(metrics_text):
        total += float(match.group(1))
    if label_fragment:
        return total
    for match in unlabeled.finditer(metrics_text):
        total += float(match.group(1))
    return total


class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path == "/metrics":
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        endpoint = request.url.path
        method = request.method
        status = str(response.status_code)

        HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=endpoint).observe(duration)
        return response


def start_push_gateway_if_configured() -> None:
    gateway = os.environ.get("LUTHOR_PROMETHEUS_PUSH_GATEWAY", "").strip()
    if not gateway:
        return

    def _push_loop() -> None:
        while not _push_stop.is_set():
            try:
                push_to_gateway(gateway, job="luthor-api", registry=REGISTRY)
            except Exception:  # pragma: no cover - network dependent
                pass
            _push_stop.wait(_PUSH_INTERVAL_SECONDS)

    global _push_thread
    _push_thread = threading.Thread(target=_push_loop, name="prometheus-push", daemon=True)
    _push_thread.start()


def stop_push_gateway() -> None:
    gateway = os.environ.get("LUTHOR_PROMETHEUS_PUSH_GATEWAY", "").strip()
    _push_stop.set()
    if _push_thread is not None:
        _push_thread.join(timeout=5)
    if gateway:
        try:
            push_to_gateway(gateway, job="luthor-api", registry=REGISTRY)
        except Exception:  # pragma: no cover - network dependent
            pass
