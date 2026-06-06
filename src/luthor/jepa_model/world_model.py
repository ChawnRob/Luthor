import torch.nn as nn

from luthor.config import EncoderConfig, MemoryConfig, PredictorConfig

from luthor.memory.context_compressor import ContextCompressor

from .encoder import Encoder
from .predictor import Predictor


class WorldModel(nn.Module):
    def __init__(
        self,
        input_dim: int,
        action_dim: int,
        encoder_config: EncoderConfig | None = None,
        predictor_config: PredictorConfig | None = None,
        memory_config: MemoryConfig | None = None,
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
        memory_config = memory_config or MemoryConfig()

        self.use_context_compression = memory_config.use_context_compression
        context_dim = encoder_config.latent_dim if self.use_context_compression else 0

        self.encoder = Encoder(
            input_dim,
            encoder_config=encoder_config,
            context_dim=context_dim,
        )
        self.predictor = Predictor(
            encoder_config.latent_dim,
            action_dim,
            predictor_config=predictor_config,
            context_dim=context_dim,
        )

        self.context_compressor: ContextCompressor | None = None
        if self.use_context_compression:
            compress_input_dim = (
                input_dim
                if memory_config.compress_source == "observation"
                else encoder_config.latent_dim
            )
            self.context_compressor = ContextCompressor(
                input_dim=compress_input_dim,
                latent_dim=encoder_config.latent_dim,
                hidden_dim=memory_config.gru_hidden_dim,
                num_layers=memory_config.gru_num_layers,
            )

        self.memory_config = memory_config
        self._latent_dim = encoder_config.latent_dim

    def encode(self, observation, context=None):
        return self.encoder(observation, context=context)

    def encode_target(self, observation):
        """Encode next observation without contextual influence (JEPA target)."""
        return self.encoder(observation, context=None)

    def predict(self, latent_state, action, context=None):
        return self.predictor(latent_state, action, context=context)

    def forward(self, observation, action, context=None):
        latent_state = self.encode(observation, context=context)
        return self.predict(latent_state, action, context=context)
