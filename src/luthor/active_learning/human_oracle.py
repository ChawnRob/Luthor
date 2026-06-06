from __future__ import annotations

import logging
from typing import Any

import torch

from luthor.active_learning.oracle import DummyOracle
from luthor.environment.gridworld import GridWorld
from luthor.prompts.loader import load_system_prompt

logger = logging.getLogger(__name__)


class HumanLabelOracle:
    """Human-in-the-loop oracle that logs the active prompt for traceability."""

    def __init__(
        self,
        env: GridWorld,
        *,
        prompt_version: str = "v1",
        fallback: DummyOracle | None = None,
    ):
        self.env = env
        self.prompt_version = prompt_version
        self.prompt_text = load_system_prompt(prompt_version)
        self.fallback = fallback or DummyOracle(env=env)

    def query(
        self,
        observation: torch.Tensor,
        action: torch.Tensor | dict[str, Any],
    ) -> torch.Tensor:
        logger.info(
            "HumanLabelOracle using prompt_version=%s | prompt=%s",
            self.prompt_version,
            self.prompt_text.strip().replace("\n", " "),
        )
        return self.fallback.query(observation, action)
