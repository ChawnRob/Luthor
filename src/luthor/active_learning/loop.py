from __future__ import annotations

import random
import uuid
from dataclasses import dataclass

import torch
import torch.optim as optim

from luthor.active_learning.human_oracle import HumanLabelOracle
from luthor.active_learning.oracle import DummyOracle
from luthor.active_learning.sample import TransitionSample
from luthor.active_learning.sampler import UncertaintySampler
from luthor.config import ActiveLearningConfig, LuthorConfig
from luthor.environment.gridworld import GridWorld, action_to_tensor
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
        env: GridWorld | None = None,
        oracle: DummyOracle | HumanLabelOracle | None = None,
    ):
        self.config = config
        self.al_config: ActiveLearningConfig = config.active_learning
        self.input_dim = self.al_config.input_dim
        self.action_dim = self.al_config.action_dim

        weather_cfg = config.tools.weather
        self.env = env or GridWorld(
            self.input_dim,
            self.action_dim,
            noise_std=0.0,
            weather_enabled=weather_cfg.enabled,
            weather_api_url=weather_cfg.api_url,
        )
        self.env.weather_enabled = weather_cfg.enabled
        self.env.weather_api_url = weather_cfg.api_url
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
                timeout_seconds=self.al_config.label_timeout_seconds,
            )
        return DummyOracle(env=self.env)

    def build_pool(self) -> list[TransitionSample]:
        pool: list[TransitionSample] = []
        observation = self.env.reset()
        weather_enabled = self.config.tools.weather.enabled and self.env.weather_enabled

        for _ in range(self.al_config.pool_size):
            use_tool = weather_enabled and random.random() < 0.25
            if use_tool:
                action: torch.Tensor | dict = {
                    "action_type": "call_tool",
                    "tool_name": "weather",
                    "tool_args": {
                        "latitude": float(observation[0].item()),
                        "longitude": float(observation[1].item()),
                    },
                }
                sample = TransitionSample(
                    observation=observation.clone(),
                    action=action,
                    sample_id=str(uuid.uuid4()),
                    used_tool=True,
                    tool_name="weather",
                    metadata={"requires_human_relevance": True},
                )
            else:
                action = torch.rand(self.action_dim) * 2 - 1
                sample = TransitionSample(
                    observation=observation.clone(),
                    action=action.clone(),
                    sample_id=str(uuid.uuid4()),
                )

            pool.append(sample)
            observation = self.env.step(action)

        return pool

    def run_round(self, round_index: int) -> ActiveLearningRoundResult:
        pool = self.build_pool()
        selected = self.sampler.select(pool, self.al_config.query_batch_size)

        uncertainties = [self.sampler.score(sample) for sample in selected]
        losses: list[float] = []

        history = (
            ContextHistory(self.config.memory.history_length)
            if self.config.memory.use_context_compression
            else None
        )
        if history is not None:
            history.add(selected[0].observation)

        for sample in selected:
            if isinstance(self.oracle, HumanLabelOracle):
                next_obs = self.oracle.query(
                    sample.observation,
                    sample.action,
                    sample_id=sample.sample_id,
                    metadata=sample.metadata,
                )
            else:
                next_obs = self.oracle.query(sample.observation, sample.action)

            action_tensor = action_to_tensor(sample.action)
            context = build_context(self.world_model, history) if history is not None else None
            for _ in range(self.al_config.train_steps_per_round):
                loss = jepa_train_step_with_context(
                    self.world_model,
                    self.optimizer,
                    sample.observation,
                    action_tensor,
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
