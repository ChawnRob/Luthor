from __future__ import annotations

import torch
import torch.nn as nn


class ContextCompressor(nn.Module):
    """
    GRU-based memory compression for observation/latent sequences.

    Produces a fixed-size context vector (latent_dim) from a variable-length history.
    """

    def __init__(
        self,
        input_dim: int,
        latent_dim: int,
        hidden_dim: int = 64,
        num_layers: int = 1,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.gru = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
        )
        self.projection = nn.Linear(hidden_dim, latent_dim)

    def compress(self, sequence: torch.Tensor) -> torch.Tensor:
        """
        Compress a sequence into a context vector.

        Args:
            sequence: Tensor of shape (seq_len, input_dim) or (batch, seq_len, input_dim)

        Returns:
            Context tensor of shape (latent_dim,) or (batch, latent_dim)
        """
        squeeze = False
        if sequence.dim() == 2:
            sequence = sequence.unsqueeze(0)
            squeeze = True
        elif sequence.dim() != 3:
            raise ValueError(f"Expected 2D or 3D sequence, got shape {tuple(sequence.shape)}")

        _output, hidden = self.gru(sequence)
        last_hidden = hidden[-1]
        context = self.projection(last_hidden)

        if squeeze:
            return context.squeeze(0)
        return context


class ContextHistory:
    """Rolling buffer of observations used to build compressed context."""

    def __init__(self, max_length: int = 8):
        self.max_length = max_length
        self._observations: list[torch.Tensor] = []

    def clear(self) -> None:
        self._observations.clear()

    def add(self, observation: torch.Tensor) -> None:
        self._observations.append(observation.detach().clone())
        if len(self._observations) > self.max_length:
            self._observations.pop(0)

    def as_sequence(self) -> torch.Tensor | None:
        if not self._observations:
            return None
        return torch.stack(self._observations)

    def compress(self, compressor: ContextCompressor) -> torch.Tensor | None:
        sequence = self.as_sequence()
        if sequence is None:
            return None
        return compressor.compress(sequence)
