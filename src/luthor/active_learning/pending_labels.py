from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

import torch


@dataclass
class PendingSample:
    sample_id: str
    observation: torch.Tensor
    action: torch.Tensor
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


class PendingLabelRegistry:
    """Thread-safe registry blocking active learning until human labels arrive."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._pending: dict[str, PendingSample] = {}
        self._events: dict[str, threading.Event] = {}
        self._labels: dict[str, dict[str, Any]] = {}

    def register(self, sample: PendingSample) -> None:
        with self._lock:
            self._pending[sample.sample_id] = sample
            self._events[sample.sample_id] = threading.Event()

    def list_pending(self) -> list[dict[str, Any]]:
        with self._lock:
            return [
                {
                    "sample_id": sample_id,
                    "observation": sample.observation.tolist(),
                    "action": sample.action.tolist(),
                    "metadata": sample.metadata,
                    "created_at": sample.created_at,
                }
                for sample_id, sample in self._pending.items()
            ]

    def submit_label(self, sample_id: str, correct_outcome: dict[str, Any]) -> bool:
        with self._lock:
            if sample_id not in self._pending:
                return False
            self._labels[sample_id] = correct_outcome
            event = self._events.get(sample_id)
            if event is not None:
                event.set()
            return True

    def wait_for_label(self, sample_id: str, timeout_seconds: float) -> dict[str, Any]:
        with self._lock:
            event = self._events.get(sample_id)
            if event is None:
                raise KeyError(f"Unknown sample_id: {sample_id}")

        if not event.wait(timeout=timeout_seconds):
            raise TimeoutError(f"Label not received for sample_id={sample_id} within {timeout_seconds}s")

        with self._lock:
            label = self._labels.pop(sample_id)
            self._pending.pop(sample_id, None)
            self._events.pop(sample_id, None)
            return label

    def clear(self) -> None:
        with self._lock:
            self._pending.clear()
            self._events.clear()
            self._labels.clear()


_registry = PendingLabelRegistry()


def get_pending_label_registry() -> PendingLabelRegistry:
    return _registry
