from __future__ import annotations

import uuid

import torch
import torch.optim as optim

from luthor.active_learning.loop import ActiveLearningLoop, ActiveLearningRoundResult
from luthor.config import ActiveLearningConfig, LuthorConfig, get_config
from luthor.jepa_model.world_model import WorldModel


class JEPAService:
    """Wraps the JEPA world model and active-learning loop for API use."""

    def __init__(self, config: LuthorConfig | None = None):
        self.config = config or get_config()
        self.input_dim = self.config.active_learning.input_dim
        self.action_dim = self.config.active_learning.action_dim

        self.world_model = WorldModel(
            self.input_dim,
            self.action_dim,
            encoder_config=self.config.encoder,
            predictor_config=self.config.predictor,
            memory_config=self.config.memory,
            latent_dim=self.config.encoder.latent_dim,
        )
        self.world_model.eval()

        self.optimizer = optim.Adam(
            self.world_model.parameters(),
            lr=self.config.planner.learning_rate,
        )
        self.active_loop = ActiveLearningLoop(
            self.config,
            world_model=self.world_model,
            optimizer=self.optimizer,
        )

    def _to_tensor(self, values: list[float], expected_dim: int, label: str) -> torch.Tensor:
        tensor = torch.tensor(values, dtype=torch.float32)
        if tensor.numel() != expected_dim:
            raise ValueError(f"{label} must have length {expected_dim}, got {tensor.numel()}")
        return tensor

    def embed(self, observation: list[float]) -> tuple[str, list[float]]:
        obs = self._to_tensor(observation, self.input_dim, "observation")
        with torch.no_grad():
            latent = self.world_model.encode(obs)
        embedding_id = str(uuid.uuid4())
        return embedding_id, latent.detach().cpu().tolist()

    def predict(
        self,
        observation: list[float],
        action: list[float],
        mc_samples: int | None = None,
    ) -> dict[str, list[float] | float]:
        obs = self._to_tensor(observation, self.input_dim, "observation")
        act = self._to_tensor(action, self.action_dim, "action")
        samples = mc_samples or self.config.active_learning.mc_samples

        with torch.no_grad():
            latent = self.world_model.encode(obs)
            mean, variance = self.world_model.predictor.predict_with_uncertainty(
                latent,
                act,
                num_samples=samples,
            )

        uncertainty = float(variance.mean().item())
        return {
            "predicted_latent": mean.detach().cpu().tolist(),
            "uncertainty": uncertainty,
            "latent_variance": variance.detach().cpu().tolist(),
        }

    def active_learn(
        self,
        num_rounds: int | None = None,
        pool_size: int | None = None,
        query_batch_size: int | None = None,
    ) -> list[ActiveLearningRoundResult]:
        al_config = ActiveLearningConfig(
            num_rounds=num_rounds or self.config.active_learning.num_rounds,
            pool_size=pool_size or self.config.active_learning.pool_size,
            query_batch_size=query_batch_size or self.config.active_learning.query_batch_size,
            mc_samples=self.config.active_learning.mc_samples,
            train_steps_per_round=self.config.active_learning.train_steps_per_round,
            input_dim=self.config.active_learning.input_dim,
            action_dim=self.config.active_learning.action_dim,
        )

        loop = ActiveLearningLoop(
            self.config,
            world_model=self.world_model,
            optimizer=self.optimizer,
        )
        loop.al_config = al_config
        loop.sampler.config = al_config

        results: list[ActiveLearningRoundResult] = []
        for round_index in range(1, al_config.num_rounds + 1):
            results.append(loop.run_round(round_index))
        return results
