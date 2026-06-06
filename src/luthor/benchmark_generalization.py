from __future__ import annotations

import random

import torch
import torch.optim as optim

from luthor.config import get_config
from luthor.environment.factory import build_environment
from luthor.jepa_model.world_model import WorldModel
from luthor.training.context_session import jepa_train_step_with_context
from luthor.utils.generalization import compute_generalization_success


def set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)


def train_on_scenarios(config, world_model, optimizer, scenarios: list[int]) -> float:
    final_loss = 0.0
    steps_per_scenario = config.generalization.train_steps_per_scenario

    for scenario_id in scenarios:
        env = build_environment(config, seed=config.seed, scenario_id=scenario_id)
        if config.environment.type == "inventory":
            observation = env.reset(scenario_id=scenario_id)
        else:
            observation = env.reset()
        for _ in range(steps_per_scenario):
            action = torch.rand(env.action_dim) * 2 - 1
            next_observation, _, _, _ = env.step(action)
            loss = jepa_train_step_with_context(
                world_model,
                optimizer,
                observation,
                action,
                next_observation,
            )
            final_loss = loss
            observation = next_observation
    return final_loss


def main() -> None:
    config = get_config()
    if config.environment.type != "inventory":
        config.environment.type = "inventory"
        inv = config.environment.inventory
        config.active_learning.input_dim = inv.num_products * 3
        config.active_learning.action_dim = inv.num_products
    set_seed(config.seed)

    env = build_environment(config)
    state_dim, action_dim = env.state_dim, env.action_dim
    world_model = WorldModel(
        state_dim,
        action_dim,
        encoder_config=config.encoder,
        predictor_config=config.predictor,
        memory_config=config.memory,
        latent_dim=config.encoder.latent_dim,
    )
    optimizer = optim.Adam(world_model.parameters(), lr=config.planner.learning_rate)

    train_loss = train_on_scenarios(
        config,
        world_model,
        optimizer,
        config.generalization.train_scenarios,
    )
    evaluation = compute_generalization_success(
        config,
        world_model,
        test_scenarios=config.generalization.test_scenarios,
    )

    print("--- Luthor Generalization Benchmark ---")
    print(f"Environment: {config.environment.type}")
    print(f"Train scenarios: {config.generalization.train_scenarios}")
    print(f"Test scenarios: {config.generalization.test_scenarios}")
    print(f"Final train loss: {train_loss:.6f}")
    print(f"generalization_success={evaluation.generalization_success:.2f}%")
    print(f"Scenario results: {evaluation.scenario_results}")


if __name__ == "__main__":
    main()
