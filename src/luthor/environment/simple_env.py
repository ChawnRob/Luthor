import torch

class SimpleEnvironment:
    def __init__(self, state_dim, action_dim):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.current_state = torch.zeros(state_dim)

    def reset(self):
        self.current_state = torch.rand(self.state_dim) * 10 - 5 # État initial aléatoire
        return self.current_state

    def step(self, action):
        # Simulation d\un dynamique simple: l\action influence l\état
        # et il y a un peu de bruit
        self.current_state = self.current_state + action * 0.5 + torch.randn(self.state_dim) * 0.1
        return self.current_state
