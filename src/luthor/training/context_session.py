from __future__ import annotations

import torch
import torch.nn as nn

from luthor.jepa_model.world_model import WorldModel
from luthor.memory.context_compressor import ContextHistory


def jepa_train_step_with_context(
    world_model: WorldModel,
    optimizer: torch.optim.Optimizer,
    observation: torch.Tensor,
    action: torch.Tensor,
    next_observation: torch.Tensor,
    context: torch.Tensor | None = None,
    loss_fn: nn.Module | None = None,
) -> float:
    """JEPA update with optional compressed context; target latent excludes context."""
    criterion = loss_fn or nn.MSELoss()

    optimizer.zero_grad()
    current_latent = world_model.encode(observation, context=context)
    target_latent = world_model.encode_target(next_observation).detach()
    predicted_latent = world_model.predict(current_latent, action, context=context)
    loss = criterion(predicted_latent, target_latent)
    loss.backward()
    optimizer.step()

    return float(loss.item())


def build_context(
    world_model: WorldModel,
    history: ContextHistory,
) -> torch.Tensor | None:
    if not world_model.use_context_compression or world_model.context_compressor is None:
        return None
    return history.compress(world_model.context_compressor)
