from __future__ import annotations

from typing import Any

from luthor.api.storage import InferenceLogStore


def compare_ab_metrics(
    log_store: InferenceLogStore,
    *,
    window_hours: int = 24,
) -> dict[str, Any]:
    rows = log_store.fetch_ab_metrics(window_hours=window_hours)
    versions: dict[str, dict[str, Any]] = {}

    for row in rows:
        version = row["model_version"] or "default"
        versions[version] = {
            "calls": int(row["calls"]),
            "mean_uncertainty": _optional_float(row.get("mean_uncertainty")),
            "mean_loss": _optional_float(row.get("mean_loss")),
            "success_rate": _optional_float(row.get("success_rate")),
        }

    for label in ("default", "candidate"):
        versions.setdefault(
            label,
            {
                "calls": 0,
                "mean_uncertainty": None,
                "mean_loss": None,
                "success_rate": None,
            },
        )

    winner = _pick_winner(versions)
    return {
        "window_hours": window_hours,
        "versions": versions,
        "winner": winner,
    }


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _pick_winner(versions: dict[str, dict[str, Any]]) -> str | None:
    default = versions.get("default", {})
    candidate = versions.get("candidate", {})

    if default.get("calls", 0) == 0 and candidate.get("calls", 0) == 0:
        return None

    default_score = _score_version(default)
    candidate_score = _score_version(candidate)
    if default_score is None and candidate_score is None:
        return None
    if candidate_score is None:
        return "default"
    if default_score is None:
        return "candidate"
    if candidate_score < default_score:
        return "candidate"
    if default_score < candidate_score:
        return "default"
    return "tie"


def _score_version(metrics: dict[str, Any]) -> float | None:
    if metrics.get("success_rate") is not None:
        return -float(metrics["success_rate"])
    if metrics.get("mean_loss") is not None:
        return float(metrics["mean_loss"])
    if metrics.get("mean_uncertainty") is not None:
        return float(metrics["mean_uncertainty"])
    return None
