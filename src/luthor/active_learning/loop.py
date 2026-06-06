from dataclasses import dataclass

import torch
import torch.optim as optim

from luthor.active_learning.oracle import DummyOracle
from luthor.active_learning.sampler import UncertaintySampler
from luthor.config import ActiveLearningConfig, LuthorConfig
from luthor.environment.simple_env import SimpleEnvironment
from luthor.jepa_model.world_model import WorldModel
from luthor.training.jepa_step import jepa_train_step


@dataclass
class ActiveLearningRoundResult:
    round_index: int
    mean_uncertainty: float
    mean_loss: float
    queried: int


class ActiveLearningLoop:
    """
    JEPA SLM skeleton active-learning loop.

    1. Build a candidate pool of (observation, action) pairs.
    2. Rank by predictor variance (uncertainty sampling).
    3. Query a dummy oracle for ground-truth next states.
    4. Fine-tune the JEPA world model on the selected batch.
    """

    def __init__(
        self,
        config: LuthorConfig,
        world_model: WorldModel | None = None,
        optimizer: optim.Optimizer | None = None,
        env: SimpleEnvironment | None = None,
        oracle: DummyOracle | None = None,
    ):
        self.config = config
        self.al_config: ActiveLearningConfig = config.active_learning
        self.input_dim = self.al_config.input_dim
        self.action_dim = self.al_config.action_dim

        self.env = env or SimpleEnvironment(self.input_dim, self.action_dim)
        self.world_model = world_model or WorldModel(
            self.input_dim,
            self.action_dim,
            encoder_config=config.encoder,
            predictor_config=config.predictor,
            latent_dim=config.encoder.latent_dim,
        )
        self.optimizer = optimizer or optim.Adam(
            self.world_model.parameters(),
            lr=config.planner.learning_rate,
        )
        self.oracle = oracle or DummyOracle(noise_std=self.env.noise_std)
        self.sampler = UncertaintySampler(self.world_model, self.al_config)

    def build_pool(self) -> list[tuple[torch.Tensor, torch.Tensor]]:
        pool: list[tuple[torch.Tensor, torch.Tensor]] = []
        observation = self.env.reset()

        for _ in range(self.al_config.pool_size):
            action = torch.rand(self.action_dim) * 2 - 1
            pool.append((observation.clone(), action.clone()))
            observation = self.env.step(action)

        return pool

    def run_round(self, round_index: int) -> ActiveLearningRoundResult:
        pool = self.build_pool()
        selected = self.sampler.select(pool, self.al_config.query_batch_size)

        uncertainties = [self.sampler.score(obs, action) for obs, action in selected]
        losses: list[float] = []

        for obs, action in selected:
            next_obs = self.oracle.query(obs, action)
            for _ in range(self.al_config.train_steps_per_round):
                loss = jepa_train_step(self.world_model, self.optimizer, obs, action, next_obs)
                losses.append(loss)

        return ActiveLearningRoundResult(
            round_index=round_index,
            mean_uncertainty=sum(uncertainties) / max(len(uncertainties), 1),
            mean_loss=sum(losses) / max(len(losses), 1),
            queried=len(selected),
        )

    def run(self) -> list[ActiveLearningRoundResult]:
        results: list[ActiveLearningRoundResult] = []
        for round_index in range(1, self.al_config.num_rounds + 1):
            result = self.run_round(round_index)
            results.append(result)
            print(
                f"Round {result.round_index}/{self.al_config.num_rounds} | "
                f"queried={result.queried} | "
                f"uncertainty={result.mean_uncertainty:.6f} | "
                f"loss={result.mean_loss:.6f}"
            )
        return results
