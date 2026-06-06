from __future__ import annotations

from dataclasses import dataclass, field

import torch

from luthor.config import LuthorConfig
from luthor.environment.factory import build_environment
from luthor.jepa_model.world_model import WorldModel


@dataclass
class GeneralizationEvaluation:
    generalization_success: float
    scenario_results: dict[int, dict[str, float]] = field(default_factory=dict)


def compute_generalization_success(
    config: LuthorConfig,
    world_model: WorldModel,
    *,
    test_scenarios: list[int] | None = None,
) -> GeneralizationEvaluation:
    scenarios = test_scenarios or config.generalization.test_scenarios
    max_steps = config.generalization.max_steps
    successes = 0
    scenario_results: dict[int, dict[str, float]] = {}

    world_model.eval()
    for scenario_id in scenarios:
        env = build_environment(config, seed=config.seed, scenario_id=scenario_id)
        observation = env.reset(scenario_id=scenario_id)
        total_cost = 0.0

        for _ in range(max_steps):
            with torch.no_grad():
                latent = world_model.encode(observation)
                action = torch.rand(env.action_dim) * 2 - 1
                _ = world_model.predict(latent, action)
            observation, reward, _, info = env.step(action)
            total_cost += float(info.get("total_cost", -reward))

        service_level = float(info.get("service_level", 0.0))
        success = service_level >= config.environment.inventory.service_level_target
        if hasattr(env, "is_successful"):
            success = env.is_successful()
        scenario_results[scenario_id] = {
            "service_level": service_level,
            "episode_cost": float(info.get("episode_cost", total_cost)),
            "success": 1.0 if success else 0.0,
        }
        if success:
            successes += 1

    rate = (successes / len(scenarios)) * 100.0 if scenarios else 0.0
    return GeneralizationEvaluation(
        generalization_success=rate,
        scenario_results=scenario_results,
    )
