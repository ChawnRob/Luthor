from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import torch
import torch.optim as optim

from luthor.active_learning.loop import ActiveLearningLoop
from luthor.environment.gridworld import GridWorld
from luthor.jepa_model.planner import Planner
from luthor.jepa_model.world_model import WorldModel
from luthor.pipeline.params import config_from_params, load_params
from luthor.utils.cost_function import euclidean_distance_cost
from luthor.utils.metrics import compute_success_rate


def set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)


def load_gridworld_spec(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def train_jepa(
    env: GridWorld,
    world_model: WorldModel,
    optimizer: optim.Optimizer,
    *,
    num_episodes: int,
    steps_per_episode: int,
) -> float:
    action_dim = env.action_dim
    final_loss = 0.0

    for _ in range(num_episodes):
        observation = env.reset()
        total_loss = 0.0

        for _ in range(steps_per_episode):
            action = torch.rand(action_dim) * 2 - 1
            next_observation = env.step(action)

            optimizer.zero_grad()
            current_latent = world_model.encoder(observation)
            target_latent = world_model.encoder(next_observation).detach()
            predicted_latent = world_model.predictor(current_latent, action)
            loss = torch.mean((predicted_latent - target_latent) ** 2)
            loss.backward()
            optimizer.step()

            total_loss += float(loss.item())
            observation = next_observation

        final_loss = total_loss / steps_per_episode

    return final_loss


def run_training(
    params_path: str | Path,
    gridworld_path: str | Path,
    metrics_path: str | Path,
) -> dict:
    params = load_params(params_path)
    config = config_from_params(params)
    set_seed(int(params.get("seed", 42)))

    grid_spec = load_gridworld_spec(gridworld_path)
    env = GridWorld.from_spec(grid_spec)

    world_model = WorldModel(
        env.state_dim,
        env.action_dim,
        encoder_config=config.encoder,
        predictor_config=config.predictor,
        latent_dim=config.encoder.latent_dim,
    )
    optimizer = optim.Adam(world_model.parameters(), lr=config.planner.learning_rate)

    eval_cfg = params.get("eval", {})
    train_steps = int(eval_cfg.get("train_steps_per_episode", 10))
    eval_episodes = int(eval_cfg.get("episodes", 5))

    train_jepa(
        env,
        world_model,
        optimizer,
        num_episodes=config.planner.num_iterations,
        steps_per_episode=train_steps,
    )

    loop = ActiveLearningLoop(
        config,
        world_model=world_model,
        optimizer=optimizer,
        env=env,
    )
    results = loop.run()
    final_loss = results[-1].mean_loss if results else 0.0

    planner = Planner(
        world_model,
        env.action_dim,
        config.planner.horizon,
        config.planner.num_samples,
        euclidean_distance_cost,
    )
    evaluation = compute_success_rate(
        env,
        planner,
        num_episodes=eval_episodes,
        max_steps=env.max_steps,
    )

    metrics = {
        "final_loss": final_loss,
        "success_rate": evaluation.success_rate,
        "steps_per_episode": evaluation.steps_per_episode,
    }

    output = Path(metrics_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)
        handle.write("\n")

    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train JEPA + active learning and export metrics.")
    parser.add_argument("params", help="Path to params.yaml")
    parser.add_argument("gridworld", help="Path to versioned GridWorld JSON")
    parser.add_argument("metrics", help="Output metrics.json path")
    args = parser.parse_args()

    metrics = run_training(args.params, args.gridworld, args.metrics)
    print(f"Training complete. metrics={metrics}")


if __name__ == "__main__":
    main()
