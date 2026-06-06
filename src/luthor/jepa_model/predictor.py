import torch
import torch.nn as nn

from luthor.config import PredictorConfig


class Predictor(nn.Module):
    def __init__(
        self,
        latent_dim: int,
        action_dim: int,
        predictor_config: PredictorConfig | None = None,
    ):
        super().__init__()
        config = predictor_config or PredictorConfig()
        self.use_attention = config.use_attention
        self.latent_dim = latent_dim

        self.latent_proj = nn.Linear(latent_dim, config.hidden_dim)
        self.action_proj = nn.Linear(action_dim, config.hidden_dim)

        if self.use_attention:
            num_heads = min(4, config.hidden_dim)
            while config.hidden_dim % num_heads != 0 and num_heads > 1:
                num_heads -= 1
            self.attention = nn.MultiheadAttention(
                embed_dim=config.hidden_dim,
                num_heads=num_heads,
                dropout=config.dropout,
                batch_first=True,
            )

        layers: list[nn.Module] = []
        for _ in range(config.num_layers):
            layers.extend(
                [
                    nn.Linear(config.hidden_dim, config.hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(config.dropout),
                ]
            )
        layers.append(nn.Linear(config.hidden_dim, latent_dim))
        self.output_network = nn.Sequential(*layers)

    def _ensure_batch(self, tensor: torch.Tensor) -> torch.Tensor:
        return tensor.unsqueeze(0) if tensor.dim() == 1 else tensor

    def forward(self, latent_state, action):
        latent_state = self._ensure_batch(latent_state)
        action = self._ensure_batch(action)

        latent_token = self.latent_proj(latent_state).unsqueeze(1)
        action_token = self.action_proj(action).unsqueeze(1)
        tokens = torch.cat([latent_token, action_token], dim=1)

        if self.use_attention:
            attended, _ = self.attention(tokens, tokens, tokens)
            x = attended.mean(dim=1)
        else:
            x = tokens.mean(dim=1)

        output = self.output_network(x)
        return output.squeeze(0) if output.shape[0] == 1 else output

    def predict_with_uncertainty(
        self,
        latent_state: torch.Tensor,
        action: torch.Tensor,
        num_samples: int = 10,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Estimate latent prediction mean and variance via MC dropout."""
        was_training = self.training
        self.train()

        samples: list[torch.Tensor] = []
        with torch.no_grad():
            for _ in range(num_samples):
                samples.append(self.forward(latent_state, action))

        if not was_training:
            self.eval()

        stacked = torch.stack(samples)
        mean = stacked.mean(dim=0)
        variance = stacked.var(dim=0, unbiased=False)
        return mean, variance
