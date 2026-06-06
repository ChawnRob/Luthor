import torch

from luthor.config import ActiveLearningConfig
from luthor.jepa_model.world_model import WorldModel


class UncertaintySampler:
    """Select transitions with highest predictor variance (MC dropout)."""

    def __init__(self, world_model: WorldModel, config: ActiveLearningConfig):
        self.world_model = world_model
        self.config = config

    def score(self, observation: torch.Tensor, action: torch.Tensor) -> float:
        with torch.no_grad():
            latent = self.world_model.encoder(observation)
            _, variance = self.world_model.predictor.predict_with_uncertainty(
                latent,
                action,
                num_samples=self.config.mc_samples,
            )
        return float(variance.mean().item())

    def select(
        self,
        pool: list[tuple[torch.Tensor, torch.Tensor]],
        query_batch_size: int | None = None,
    ) -> list[tuple[torch.Tensor, torch.Tensor]]:
        batch_size = query_batch_size or self.config.query_batch_size
        scored = [(self.score(obs, action), obs, action) for obs, action in pool]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [(obs, action) for _, obs, action in scored[:batch_size]]
