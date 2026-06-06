import torch

from luthor.environment.gridworld import GridWorld


class DummyOracle:
    """Ground-truth labeler backed by GridWorld dynamics."""

    def __init__(self, env: GridWorld | None = None, noise_std: float = 0.1):
        self.env = env
        self.noise_std = env.noise_std if env is not None else noise_std

    def query(self, observation: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        """Return the true next observation for a (state, action) pair."""
        if self.env is not None:
            return GridWorld._apply_transition(
                observation,
                action,
                noise_std=self.env.noise_std,
                grid_size=self.env.grid_size,
                obstacle_set=self.env.obstacle_set,
            )
        return GridWorld.transition(observation, action, self.noise_std)
