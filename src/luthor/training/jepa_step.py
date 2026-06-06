import torch
import torch.nn as nn

from luthor.jepa_model.world_model import WorldModel


def jepa_train_step(
    world_model: WorldModel,
    optimizer: torch.optim.Optimizer,
    observation: torch.Tensor,
    action: torch.Tensor,
    next_observation: torch.Tensor,
    loss_fn: nn.Module | None = None,
) -> float:
    """Single JEPA update: predict next latent from current latent and action."""
    criterion = loss_fn or nn.MSELoss()

    optimizer.zero_grad()
    current_latent = world_model.encoder(observation)
    target_latent = world_model.encoder(next_observation).detach()
    predicted_latent = world_model.predictor(current_latent, action)
    loss = criterion(predicted_latent, target_latent)
    loss.backward()
    optimizer.step()

    return float(loss.item())
