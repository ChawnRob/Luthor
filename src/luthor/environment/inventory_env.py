from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any

import torch

from luthor.config import InventoryConfig


@dataclass
class InventoryStepInfo:
    demand: list[float]
    stockout: list[float]
    holding_cost: float
    stockout_cost: float
    total_cost: float
    service_level: float


class InventoryEnv:
    """
    Multi-product inventory management environment.

    Observation (length 3 * num_products):
      [stock, last_demand, pipeline_incoming]

    Action (length num_products):
      order quantities mapped from [-1, 1] to [0, max_order].
    """

    def __init__(
        self,
        config: InventoryConfig,
        *,
        seed: int | None = None,
        scenario_id: int = 0,
    ):
        self.config = config
        self.num_products = config.num_products
        self.state_dim = self.num_products * 3
        self.action_dim = self.num_products
        self.max_steps = config.max_steps
        self.scenario_id = scenario_id
        self._rng = random.Random(seed)

        self._step = 0
        self._stock = [0.0] * self.num_products
        self._last_demand = [0.0] * self.num_products
        self._pipeline: list[list[float]] = [
            [0.0] * self.num_products for _ in range(config.lead_time)
        ]
        self._total_cost = 0.0
        self._total_demand = 0.0
        self._total_fulfilled = 0.0

    @classmethod
    def from_config(
        cls,
        config: InventoryConfig,
        *,
        seed: int | None = None,
        scenario_id: int = 0,
    ) -> InventoryEnv:
        return cls(config, seed=seed, scenario_id=scenario_id)

    def reset(self, *, scenario_id: int | None = None) -> torch.Tensor:
        if scenario_id is not None:
            self.scenario_id = scenario_id
        self._step = 0
        self._total_cost = 0.0
        self._total_demand = 0.0
        self._total_fulfilled = 0.0
        self._pipeline = [
            [0.0] * self.num_products for _ in range(self.config.lead_time)
        ]
        initial = self.config.initial_stock or [mean * 2 for mean in self.config.demand_mean]
        self._stock = [float(initial[i]) for i in range(self.num_products)]
        self._last_demand = [0.0] * self.num_products
        return self._observation_tensor()

    def step(self, action: torch.Tensor) -> tuple[torch.Tensor, float, bool, dict[str, Any]]:
        self._step += 1
        order = self._decode_action(action)

        if self.config.lead_time > 0:
            arriving = self._pipeline.pop(0)
            self._pipeline.append([0.0] * self.num_products)
            for idx in range(self.num_products):
                self._stock[idx] += arriving[idx]

        demand = self._sample_demand()
        self._last_demand = demand

        stockout_units = [0.0] * self.num_products
        for idx in range(self.num_products):
            fulfilled = min(self._stock[idx], demand[idx])
            stockout_units[idx] = max(0.0, demand[idx] - fulfilled)
            self._stock[idx] = max(0.0, self._stock[idx] - demand[idx])
            self._total_demand += demand[idx]
            self._total_fulfilled += fulfilled

        holding_cost = sum(self._stock) * self.config.holding_cost
        stockout_cost = sum(stockout_units) * self.config.stockout_cost
        step_cost = holding_cost + stockout_cost
        self._total_cost += step_cost

        if self.config.lead_time > 0:
            self._pipeline[-1] = [self._pipeline[-1][i] + order[i] for i in range(self.num_products)]

        service_level = (
            self._total_fulfilled / self._total_demand if self._total_demand > 0 else 1.0
        )
        reward = -step_cost
        if service_level >= self.config.service_level_target:
            reward += 1.0

        done = self._step >= self.max_steps
        info = {
            "demand": demand,
            "stockout": stockout_units,
            "holding_cost": holding_cost,
            "stockout_cost": stockout_cost,
            "total_cost": step_cost,
            "service_level": service_level,
            "episode_cost": self._total_cost,
        }
        return self._observation_tensor(), reward, done, info

    def predict_next_observation(
        self,
        observation: torch.Tensor,
        action: torch.Tensor,
    ) -> torch.Tensor:
        clone = self.clone()
        clone.set_observation(observation)
        next_obs, _, _, _ = clone.step(action)
        return next_obs

    def set_observation(self, observation: torch.Tensor) -> None:
        values = observation.detach().cpu().tolist()
        n = self.num_products
        self._stock = [float(values[i]) for i in range(n)]
        self._last_demand = [float(values[n + i]) for i in range(n)]
        pipeline = [float(values[2 * n + i]) for i in range(n)]
        if self.config.lead_time > 0:
            self._pipeline[-1] = pipeline

    def clone(self) -> InventoryEnv:
        copied = InventoryEnv(
            self.config,
            seed=None,
            scenario_id=self.scenario_id,
        )
        copied._step = self._step
        copied._stock = list(self._stock)
        copied._last_demand = list(self._last_demand)
        copied._pipeline = [list(row) for row in self._pipeline]
        copied._total_cost = self._total_cost
        copied._total_demand = self._total_demand
        copied._total_fulfilled = self._total_fulfilled
        copied._rng.setstate(self._rng.getstate())
        return copied

    def is_successful(self) -> bool:
        service_level = (
            self._total_fulfilled / self._total_demand if self._total_demand > 0 else 1.0
        )
        return service_level >= self.config.service_level_target

    def to_spec(self) -> dict[str, Any]:
        return {
            "type": "inventory",
            "state_dim": self.state_dim,
            "action_dim": self.action_dim,
            "scenario_id": self.scenario_id,
            **self.config.__dict__,
        }

    def _observation_tensor(self) -> torch.Tensor:
        pipeline = self._pipeline[-1] if self.config.lead_time > 0 else [0.0] * self.num_products
        values = self._stock + self._last_demand + pipeline
        return torch.tensor(values, dtype=torch.float32)

    def _decode_action(self, action: torch.Tensor) -> list[float]:
        action_values = action.detach().cpu().tolist()
        if isinstance(action_values, float):
            action_values = [action_values]
        orders: list[float] = []
        for value in action_values[: self.num_products]:
            normalized = (float(value) + 1.0) / 2.0
            orders.append(max(0.0, normalized * self.config.max_order))
        while len(orders) < self.num_products:
            orders.append(0.0)
        return orders

    def _sample_demand(self) -> list[float]:
        demands: list[float] = []
        for idx in range(self.num_products):
            base_mean = self.config.demand_mean[idx]
            base_std = self.config.demand_std[idx]
            mean = self._scenario_mean(base_mean, idx)
            if self.config.demand_distribution == "poisson":
                value = self._rng.poisson(max(mean, 0.0))
            else:
                value = self._rng.gauss(mean, base_std)
            demands.append(max(0.0, float(value)))
        return demands

    def _scenario_mean(self, base_mean: float, product_idx: int) -> float:
        step = self._step
        scenario = self.scenario_id
        if scenario == 0:
            return base_mean
        if scenario == 1:
            seasonal = 1.0 + 0.3 * math.sin(step / 5.0 + product_idx)
            return base_mean * seasonal
        if scenario == 2:
            shock = 2.5 if self._rng.random() < 0.15 else 1.0
            return base_mean * shock
        if scenario == 3:
            return base_mean * (1.0 + 0.02 * step)
        if scenario == 4:
            return base_mean * 1.4
        if scenario == 5:
            return base_mean * 0.6
        return base_mean * (1.0 + 0.05 * (scenario % 3))
