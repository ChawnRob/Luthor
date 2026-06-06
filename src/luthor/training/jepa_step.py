import torch
import torch.nn as nn

from luthor.jepa_model.world_model import WorldModel
from luthor.training.context_session import jepa_train_step_with_context


def jepa_train_step(
    world_model: WorldModel,
    optimizer: torch.optim.Optimizer,
    observation: torch.Tensor,
    action: torch.Tensor,
    next_observation: torch.Tensor,
    loss_fn: nn.Module | None = None,
    context: torch.Tensor | None = None,
) -> float:
    """Single JEPA update with optional compressed context."""
    return jepa_train_step_with_context(
        world_model,
        optimizer,
        observation,
        action,
        next_observation,
        context=context,
        loss_fn=loss_fn,
    )
