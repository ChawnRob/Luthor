from __future__ import annotations

import logging
import uuid
from typing import Any

import torch

from luthor.active_learning.oracle import DummyOracle
from luthor.active_learning.pending_labels import (
    PendingLabelRegistry,
    PendingSample,
    get_pending_label_registry,
)
from luthor.prompts.loader import load_system_prompt

logger = logging.getLogger(__name__)


class HumanLabelOracle:
    """Blocks until a human label is submitted, with optional mock fallback."""

    def __init__(
        self,
        env,
        *,
        prompt_version: str = "v1",
        registry: PendingLabelRegistry | None = None,
        timeout_seconds: int = 3600,
        use_mock_human: bool = True,
        fallback: DummyOracle | None = None,
    ):
        self.env = env
        self.prompt_version = prompt_version
        self.prompt_text = load_system_prompt(prompt_version)
        self.registry = registry or get_pending_label_registry()
        self.timeout_seconds = timeout_seconds
        self.use_mock_human = use_mock_human
        self.fallback = fallback or DummyOracle(env=env)

    def query(
        self,
        observation: torch.Tensor,
        action: torch.Tensor,
        *,
        sample_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> torch.Tensor:
        logger.info(
            "HumanLabelOracle prompt_version=%s | prompt=%s",
            self.prompt_version,
            self.prompt_text.strip().replace("\n", " "),
        )

        if self.use_mock_human:
            return self.fallback.query(observation, action)

        sample_id = sample_id or str(uuid.uuid4())
        suggested = self.fallback.query(observation, action)
        sample_metadata = {
            **(metadata or {}),
            "suggested_next_observation": suggested.tolist(),
        }
        pending = PendingSample(
            sample_id=sample_id,
            observation=observation,
            action=action,
            metadata=sample_metadata,
        )
        self.registry.register(pending)
        outcome = self.registry.wait_for_label(sample_id, self.timeout_seconds)
        next_observation = outcome.get("next_observation")
        if next_observation is None:
            raise ValueError("correct_outcome must include 'next_observation'")
        return torch.tensor(next_observation, dtype=torch.float32)
