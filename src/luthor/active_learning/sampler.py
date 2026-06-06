from __future__ import annotations

import torch

from luthor.active_learning.sample import TransitionSample
from luthor.config import ActiveLearningConfig
from luthor.environment.gridworld import action_to_tensor
from luthor.jepa_model.world_model import WorldModel

TOOL_SAMPLE_BOOST = 10.0


class UncertaintySampler:
    """Select transitions with highest predictor variance (MC dropout)."""

    def __init__(self, world_model: WorldModel, config: ActiveLearningConfig):
        self.world_model = world_model
        self.config = config

    def score(self, sample: TransitionSample) -> float:
        action_tensor = action_to_tensor(sample.action)
        with torch.no_grad():
            latent = self.world_model.encoder(sample.observation)
            _, variance = self.world_model.predictor.predict_with_uncertainty(
                latent,
                action_tensor,
                num_samples=self.config.mc_samples,
            )
        base_score = float(variance.mean().item())
        if sample.used_tool and self.config.human_in_loop:
            return base_score + TOOL_SAMPLE_BOOST
        return base_score

    def select(
        self,
        pool: list[TransitionSample],
        query_batch_size: int | None = None,
    ) -> list[TransitionSample]:
        batch_size = query_batch_size or self.config.query_batch_size
        scored = [(self.score(sample), sample) for sample in pool]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [sample for _, sample in scored[:batch_size]]
