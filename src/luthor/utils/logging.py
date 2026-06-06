from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_run_log(
    *,
    hyperparameters: dict[str, Any],
    final_loss: float,
    success_rate: float,
    steps_per_episode: list[int],
    run_type: str,
    timestamp: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a structured JSON-serializable run log payload."""
    payload: dict[str, Any] = {
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        "run_type": run_type,
        "hyperparameters": hyperparameters,
        "final_loss": final_loss,
        "success_rate": success_rate,
        "steps_per_episode": steps_per_episode,
    }
    if extra:
        payload.update(extra)
    return payload


def write_run_log(path: str | Path, payload: dict[str, Any]) -> Path:
    """Write a structured run log to disk as JSON."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    return output_path
