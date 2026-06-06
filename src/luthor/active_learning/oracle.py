import torch

from luthor.environment.simple_env import SimpleEnvironment


class DummyOracle:
    """Ground-truth labeler backed by the simple environment dynamics."""

    def __init__(self, noise_std: float = 0.1):
        self.noise_std = noise_std

    def query(self, observation: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        """Return the true next observation for a (state, action) pair."""
        return SimpleEnvironment.transition(observation, action, self.noise_std)
