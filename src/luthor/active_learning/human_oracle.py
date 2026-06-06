from __future__ import annotations

import uuid
from typing import Any

import torch

from luthor.active_learning.pending_labels import PendingLabelRegistry, PendingSample, get_pending_label_registry
from luthor.environment.gridworld import GridWorld


class HumanLabelOracle:
    """Blocks until a human label is submitted for each queried sample."""

    def __init__(
        self,
        env: GridWorld,
        registry: PendingLabelRegistry | None = None,
        timeout_seconds: int = 3600,
    ):
        self.env = env
        self.registry = registry or get_pending_label_registry()
        self.timeout_seconds = timeout_seconds

    def request_and_wait(
        self,
        observation: torch.Tensor,
        action: torch.Tensor | dict[str, Any],
        *,
        sample_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[torch.Tensor, str]:
        sample_id = sample_id or str(uuid.uuid4())
        pending = PendingSample(
            sample_id=sample_id,
            observation=observation,
            action=action,
            metadata=metadata or {},
        )
        self.registry.register(pending)
        outcome = self.registry.wait_for_label(sample_id, self.timeout_seconds)
        next_observation = outcome.get("next_observation")
        if next_observation is None:
            raise ValueError("correct_outcome must include 'next_observation'")
        return torch.tensor(next_observation, dtype=torch.float32), sample_id

    def query(
        self,
        observation: torch.Tensor,
        action: torch.Tensor | dict[str, Any],
        *,
        sample_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> torch.Tensor:
        next_obs, _ = self.request_and_wait(
            observation,
            action,
            sample_id=sample_id,
            metadata=metadata,
        )
        return next_obs
