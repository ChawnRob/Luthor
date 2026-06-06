import torch
import torch.nn as nn

from luthor.config import EncoderConfig


class Encoder(nn.Module):
    def __init__(
        self,
        input_dim: int,
        encoder_config: EncoderConfig | None = None,
        latent_dim: int | None = None,
        *,
        context_dim: int = 0,
    ):
        super().__init__()
        config = encoder_config or EncoderConfig()
        if latent_dim is not None:
            config = EncoderConfig(
                latent_dim=latent_dim,
                hidden_dim=config.hidden_dim,
                num_layers=config.num_layers,
                dropout=config.dropout,
            )

        self.latent_dim = config.latent_dim
        self.context_dim = context_dim
        self.obs_network = self._build_network(input_dim, config)
        if context_dim > 0:
            self.contextual_network = self._build_network(input_dim + context_dim, config)
        else:
            self.contextual_network = None

    def _build_network(self, in_dim: int, config: EncoderConfig) -> nn.Sequential:
        layers: list[nn.Module] = [
            nn.Linear(in_dim, config.hidden_dim),
            nn.ReLU(),
            nn.Dropout(config.dropout),
        ]
        for _ in range(config.num_layers - 1):
            layers.extend(
                [
                    nn.Linear(config.hidden_dim, config.hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(config.dropout),
                ]
            )
        layers.append(nn.Linear(config.hidden_dim, config.latent_dim))
        return nn.Sequential(*layers)

    def forward(self, x: torch.Tensor, context: torch.Tensor | None = None) -> torch.Tensor:
        if context is not None and self.contextual_network is not None:
            return self.contextual_network(torch.cat([x, context], dim=-1))
        return self.obs_network(x)
