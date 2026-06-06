import torch.nn as nn

from luthor.config import EncoderConfig, PredictorConfig

from .encoder import Encoder
from .predictor import Predictor


class WorldModel(nn.Module):
    def __init__(
        self,
        input_dim: int,
        action_dim: int,
        encoder_config: EncoderConfig | None = None,
        predictor_config: PredictorConfig | None = None,
        latent_dim: int | None = None,
    ):
        super().__init__()
        encoder_config = encoder_config or EncoderConfig()
        if latent_dim is not None:
            encoder_config = EncoderConfig(
                latent_dim=latent_dim,
                hidden_dim=encoder_config.hidden_dim,
                num_layers=encoder_config.num_layers,
                dropout=encoder_config.dropout,
            )

        predictor_config = predictor_config or PredictorConfig()
        self.encoder = Encoder(input_dim, encoder_config=encoder_config)
        self.predictor = Predictor(
            encoder_config.latent_dim,
            action_dim,
            predictor_config=predictor_config,
        )

    def forward(self, observation, action):
        latent_state = self.encoder(observation)
        predicted_latent_state = self.predictor(latent_state, action)
        return predicted_latent_state
