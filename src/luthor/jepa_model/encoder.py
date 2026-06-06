import torch.nn as nn

from luthor.config import EncoderConfig


class Encoder(nn.Module):
    def __init__(
        self,
        input_dim: int,
        encoder_config: EncoderConfig | None = None,
        latent_dim: int | None = None,
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
        layers: list[nn.Module] = [
            nn.Linear(input_dim, config.hidden_dim),
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
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)
