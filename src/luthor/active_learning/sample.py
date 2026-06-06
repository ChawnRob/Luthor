from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import torch


@dataclass
class TransitionSample:
    """A candidate transition for active learning."""

    observation: torch.Tensor
    action: torch.Tensor | dict[str, Any]
    sample_id: str
    used_tool: bool = False
    tool_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
