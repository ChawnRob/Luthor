from __future__ import annotations

import random
from dataclasses import dataclass

import torch
import torch.optim as optim

from luthor.active_learning.human_oracle import HumanLabelOracle
from luthor.active_learning.oracle import DummyOracle
from luthor.active_learning.sampler import UncertaintySampler
from luthor.config import ActiveLearningConfig, LuthorConfig
from luthor.environment.factory import build_environment
from luthor.jepa_model.world_model import WorldModel
from luthor.memory.context_compressor import ContextHistory
from luthor.training.context_session import build_context, jepa_train_step_with_context


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
    3. Query oracle (dummy or human-in-the-loop) for ground-truth next states.
    4. Fine-tune the JEPA world model on the selected batch.
    """

    def __init__(
        self,
        config: LuthorConfig,
        world_model: WorldModel | None = None,
        optimizer: optim.Optimizer | None = None,
        env=None,
        oracle: DummyOracle | HumanLabelOracle | None = None,
    ):
        self.config = config
        self.al_config: ActiveLearningConfig = config.active_learning
        self.input_dim = self.al_config.input_dim
        self.action_dim = self.al_config.action_dim

        self.env = env or build_environment(config, seed=config.seed)
        self.input_dim = self.env.state_dim
        self.action_dim = self.env.action_dim

        self.world_model = world_model or WorldModel(
            self.input_dim,
            self.action_dim,
            encoder_config=config.encoder,
            predictor_config=config.predictor,
            memory_config=config.memory,
            latent_dim=config.encoder.latent_dim,
        )
        self.optimizer = optimizer or optim.Adam(
            self.world_model.parameters(),
            lr=config.planner.learning_rate,
        )
        self.oracle = oracle or self._build_oracle()
        self.sampler = UncertaintySampler(self.world_model, self.al_config)

    def _build_oracle(self) -> DummyOracle | HumanLabelOracle:
        if self.al_config.human_in_loop:
            return HumanLabelOracle(
                env=self.env,
                prompt_version=self.config.prompt_version,
                use_mock_human=self.al_config.use_mock_human,
            )
        return DummyOracle(env=self.env)

    def build_pool(self) -> list[tuple[torch.Tensor, torch.Tensor]]:
        pool: list[tuple[torch.Tensor, torch.Tensor]] = []
        scenario_id = random.choice(self.config.generalization.train_scenarios)
        if self.config.environment.type == "inventory":
            observation = self.env.reset(scenario_id=scenario_id)
        else:
            observation = self.env.reset()

        for _ in range(self.al_config.pool_size):
            action = torch.rand(self.action_dim) * 2 - 1
            pool.append((observation.clone(), action.clone()))
            if hasattr(self.env, "step"):
                result = self.env.step(action)
                observation = result[0] if isinstance(result, tuple) else result
            else:
                observation = self.oracle.query(observation, action)

        return pool

    def run_round(self, round_index: int) -> ActiveLearningRoundResult:
        pool = self.build_pool()
        selected = self.sampler.select(pool, self.al_config.query_batch_size)

        uncertainties = [self.sampler.score(obs, action) for obs, action in selected]
        losses: list[float] = []

        history = (
            ContextHistory(self.config.memory.history_length)
            if self.config.memory.use_context_compression
            else None
        )
        if history is not None:
            history.add(selected[0][0])

        for obs, action in selected:
            next_obs = self.oracle.query(
                obs,
                action,
                metadata={"environment": self.config.environment.type},
            ) if isinstance(self.oracle, HumanLabelOracle) else self.oracle.query(obs, action)

            context = build_context(self.world_model, history) if history is not None else None
            for _ in range(self.al_config.train_steps_per_round):
                loss = jepa_train_step_with_context(
                    self.world_model,
                    self.optimizer,
                    obs,
                    action,
                    next_obs,
                    context=context,
                )
                losses.append(loss)
            if history is not None:
                history.add(next_obs)

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
