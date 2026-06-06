from __future__ import annotations

import os
import threading
from typing import Any

_lock = threading.Lock()
_model: Any | None = None


def is_enabled() -> bool:
    return os.getenv("LUTHOR_SLM_FALLBACK_ENABLED", "true").lower() == "true"


def model_path() -> str:
    return os.getenv(
        "LUTHOR_SLM_MODEL_PATH",
        os.getenv("LUTHOR_SMOLLM_MODEL_PATH", "./models/SmolLM3-3B-Q4_K_M.gguf"),
    )


def _get_model() -> Any:
    global _model
    if _model is not None:
        return _model

    with _lock:
        if _model is not None:
            return _model
        try:
            from llama_cpp import Llama
        except ImportError as exc:
            raise RuntimeError(
                "llama-cpp-python is required for SLM fallback: pip install llama-cpp-python"
            ) from exc

        path = model_path()
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"SmolLM3 model not found at {path}. "
                "Set LUTHOR_SLM_MODEL_PATH to a local GGUF file."
            )

        _model = Llama(
            model_path=path,
            n_ctx=int(os.getenv("LUTHOR_SLM_N_CTX", "4096")),
            n_threads=int(os.getenv("LUTHOR_SLM_N_THREADS", "4")),
            verbose=False,
        )
        return _model


def complete(prompt: str, system_prompt: str | None = None) -> str:
    """On-demand SmolLM3 completion (model loaded lazily, no permanent service)."""
    if not is_enabled():
        raise RuntimeError("SLM fallback is disabled (LUTHOR_SLM_FALLBACK_ENABLED=false)")

    model = _get_model()
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = model.create_chat_completion(
        messages=messages,
        temperature=float(os.getenv("LUTHOR_SLM_TEMPERATURE", "0.2")),
        max_tokens=int(os.getenv("LUTHOR_SLM_MAX_TOKENS", "512")),
    )
    choice = response["choices"][0]["message"]["content"]
    return str(choice).strip()


def unload() -> None:
    """Release the in-process model (optional memory cleanup)."""
    global _model
    with _lock:
        _model = None


def reset_for_tests() -> None:
    unload()
