import torch
import torch.nn as nn

class Predictor(nn.Module):
    def __init__(self, latent_dim, action_dim):
        super(Predictor, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(latent_dim + action_dim, 128),
            nn.ReLU(),
            nn.Linear(128, latent_dim)
        )

    def forward(self, latent_state, action):
        # Concaténer l'état latent et l'action pour la prédiction
        x = torch.cat([latent_state, action], dim=-1)
        return self.network(x)
