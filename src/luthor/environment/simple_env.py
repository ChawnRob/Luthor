import torch


class SimpleEnvironment:
    def __init__(self, state_dim, action_dim, noise_std: float = 0.1):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.noise_std = noise_std
        self.current_state = torch.zeros(state_dim)

    @staticmethod
    def transition(state: torch.Tensor, action: torch.Tensor, noise_std: float = 0.1) -> torch.Tensor:
        """Apply environment dynamics without mutating simulator state."""
        return state + action * 0.5 + torch.randn_like(state) * noise_std

    def reset(self):
        self.current_state = torch.rand(self.state_dim) * 10 - 5
        return self.current_state

    def step(self, action):
        self.current_state = self.transition(self.current_state, action, self.noise_std)
        return self.current_state
