from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from luthor.config import PredictorConfig


def apply_feature_map(x: torch.Tensor, feature_map: str) -> torch.Tensor:
    if feature_map == "elu+1":
        return F.elu(x) + 1.0
    if feature_map == "relu":
        return F.relu(x) + 1e-6
    raise ValueError(f"Unsupported feature map: {feature_map}")


class LinearAttention(nn.Module):
    """
    Linear-time attention via a positive feature map (Performer / FAVOR+ style).

    Complexity is O(N * d^2) in sequence length N and head dimension d.
    """

    def __init__(
        self,
        dim: int,
        num_heads: int,
        feature_map: str = "elu+1",
        dropout: float = 0.0,
    ):
        super().__init__()
        if dim % num_heads != 0:
            raise ValueError(f"dim={dim} must be divisible by num_heads={num_heads}")

        self.dim = dim
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        self.feature_map = feature_map

        self.q_proj = nn.Linear(dim, dim)
        self.k_proj = nn.Linear(dim, dim)
        self.v_proj = nn.Linear(dim, dim)
        self.out_proj = nn.Linear(dim, dim)
        self.dropout = nn.Dropout(dropout)

    def _split_heads(self, tensor: torch.Tensor) -> torch.Tensor:
        batch, seq_len, _ = tensor.shape
        return tensor.view(batch, seq_len, self.num_heads, self.head_dim).transpose(1, 2)

    def _merge_heads(self, tensor: torch.Tensor) -> torch.Tensor:
        batch, _, seq_len, _ = tensor.shape
        return tensor.transpose(1, 2).contiguous().view(batch, seq_len, self.dim)

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
    ) -> torch.Tensor:
        query = self.q_proj(query)
        key = self.k_proj(key)
        value = self.v_proj(value)

        query_heads = self._split_heads(query)
        key_heads = self._split_heads(key)
        value_heads = self._split_heads(value)

        query_feat = apply_feature_map(query_heads, self.feature_map)
        key_feat = apply_feature_map(key_heads, self.feature_map)

        kv = torch.einsum("bhmd,bhme->bhde", key_feat, value_heads)
        numerator = torch.einsum("bhnd,bhde->bhne", query_feat, kv)

        key_sum = key_feat.sum(dim=2)
        denominator = torch.einsum("bhne,bhe->bhn", query_feat, key_sum).unsqueeze(-1)
        denominator = denominator.clamp(min=1e-6)

        attended = numerator / denominator
        output = self._merge_heads(attended)
        return self.out_proj(self.dropout(output))


class SubquadraticPredictor(nn.Module):
    """JEPA predictor using linear attention over latent, action, and context tokens."""

    def __init__(
        self,
        latent_dim: int,
        action_dim: int,
        predictor_config: PredictorConfig | None = None,
        *,
        context_dim: int = 0,
    ):
        super().__init__()
        config = predictor_config or PredictorConfig()
        self.latent_dim = latent_dim
        self.context_dim = context_dim

        hidden_dim = config.hidden_dim
        num_heads = config.linear_attention_heads
        while hidden_dim % num_heads != 0 and num_heads > 1:
            num_heads -= 1

        dim_head = config.linear_attention_dim_head
        if dim_head * num_heads != hidden_dim:
            hidden_dim = dim_head * num_heads

        self.hidden_dim = hidden_dim
        self.latent_proj = nn.Linear(latent_dim, hidden_dim)
        self.action_proj = nn.Linear(action_dim, hidden_dim)
        self.context_proj = (
            nn.Linear(context_dim, hidden_dim) if context_dim > 0 else None
        )

        self.attention = LinearAttention(
            dim=hidden_dim,
            num_heads=num_heads,
            feature_map=config.feature_map,
            dropout=config.dropout,
        )

        layers: list[nn.Module] = []
        for _ in range(config.num_layers):
            layers.extend(
                [
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(config.dropout),
                ]
            )
        layers.append(nn.Linear(hidden_dim, latent_dim))
        self.output_network = nn.Sequential(*layers)

    def _ensure_batch(self, tensor: torch.Tensor) -> torch.Tensor:
        return tensor.unsqueeze(0) if tensor.dim() == 1 else tensor

    def _context_tokens(self, context: torch.Tensor, batch_size: int) -> torch.Tensor:
        if context.dim() == 1:
            context = context.unsqueeze(0)
            return self.context_proj(context).unsqueeze(1)
        if context.dim() == 2:
            if batch_size == 1 and context.shape[-1] == self.context_dim:
                batched = context.unsqueeze(0)
                if batched.shape[1] == 1:
                    return self.context_proj(batched.squeeze(1)).unsqueeze(1)
                return self.context_proj(batched)
            return self.context_proj(context).unsqueeze(1)
        if context.dim() == 3:
            return self.context_proj(context)
        raise ValueError("context must be a vector or a sequence tensor")

    def _build_tokens(
        self,
        latent_state: torch.Tensor,
        action: torch.Tensor,
        context: torch.Tensor | None,
    ) -> torch.Tensor:
        latent_state = self._ensure_batch(latent_state)
        action = self._ensure_batch(action)

        tokens = [
            self.latent_proj(latent_state).unsqueeze(1),
            self.action_proj(action).unsqueeze(1),
        ]

        if context is not None and self.context_proj is not None:
            tokens.append(self._context_tokens(context, latent_state.shape[0]))

        return torch.cat(tokens, dim=1)

    def forward(
        self,
        latent_state: torch.Tensor,
        action: torch.Tensor,
        context: torch.Tensor | None = None,
    ) -> torch.Tensor:
        token_tensor = self._build_tokens(latent_state, action, context)
        query = token_tensor[:, :1, :]
        attended = self.attention(query, token_tensor, token_tensor)
        output = self.output_network(attended.squeeze(1))
        return output.squeeze(0) if output.shape[0] == 1 else output

    def predict_with_uncertainty(
        self,
        latent_state: torch.Tensor,
        action: torch.Tensor,
        num_samples: int = 10,
        context: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        was_training = self.training
        self.train()

        samples: list[torch.Tensor] = []
        with torch.no_grad():
            for _ in range(num_samples):
                samples.append(self.forward(latent_state, action, context=context))

        if not was_training:
            self.eval()

        stacked = torch.stack(samples)
        mean = stacked.mean(dim=0)
        variance = stacked.var(dim=0, unbiased=False)
        return mean, variance
