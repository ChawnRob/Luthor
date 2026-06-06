from __future__ import annotations

import torch

from luthor.environment.gridworld import GridWorld
from luthor.environment.inventory_env import InventoryEnv


class DummyOracle:
    """Ground-truth labeler backed by environment dynamics."""

    def __init__(self, env=None, noise_std: float = 0.1):
        self.env = env
        self.noise_std = getattr(env, "noise_std", noise_std) if env is not None else noise_std

    def query(self, observation: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        """Return the true next observation for a (state, action) pair."""
        if self.env is not None and hasattr(self.env, "predict_next_observation"):
            return self.env.predict_next_observation(observation, action)

        if isinstance(self.env, GridWorld):
            return GridWorld._apply_transition(
                observation,
                action,
                noise_std=self.env.noise_std,
                grid_size=self.env.grid_size,
                obstacle_set=self.env.obstacle_set,
            )

        if isinstance(self.env, InventoryEnv):
            return self.env.predict_next_observation(observation, action)

        return GridWorld.transition(observation, action, self.noise_std)
