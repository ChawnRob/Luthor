from .encoder import Encoder
from .predictor import Predictor
import torch.nn as nn

class WorldModel(nn.Module):
    def __init__(self, input_dim, latent_dim, action_dim):
        super(WorldModel, self).__init__()
        self.encoder = Encoder(input_dim, latent_dim)
        self.predictor = Predictor(latent_dim, action_dim)

    def forward(self, observation, action):
        latent_state = self.encoder(observation)
        predicted_latent_state = self.predictor(latent_state, action)
        return predicted_latent_state
