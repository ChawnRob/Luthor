import os

import matplotlib

matplotlib.use("Agg")

import torch
import torch.optim as optim

from luthor.config import get_config
from luthor.environment.simple_env import SimpleEnvironment
from luthor.jepa_model.planner import Planner
from luthor.jepa_model.world_model import WorldModel
from luthor.utils.cost_function import euclidean_distance_cost
from luthor.utils.visualizer import Visualizer


def main():
    config = get_config()

    input_dim = 2
    action_dim = 2
    latent_dim = config.encoder.latent_dim
    horizon = config.planner.horizon
    num_samples = config.planner.num_samples
    learning_rate = config.planner.learning_rate
    num_episodes = config.planner.num_iterations

    os.makedirs(config.visualization.output_dir, exist_ok=True)

    env = SimpleEnvironment(input_dim, action_dim)
    world_model = WorldModel(
        input_dim,
        action_dim,
        encoder_config=config.encoder,
        predictor_config=config.predictor,
        latent_dim=latent_dim,
    )
    optimizer = optim.Adam(world_model.parameters(), lr=learning_rate)
    planner = Planner(world_model, action_dim, horizon, num_samples, euclidean_distance_cost)

    print("--- Phase 1: Apprentissage du Modèle du Monde (Luthor) ---")
    for episode in range(num_episodes):
        obs = env.reset()
        total_loss = 0
        for _ in range(10):
            action = torch.rand(action_dim) * 2 - 1
            next_obs = env.step(action)

            optimizer.zero_grad()
            current_latent = world_model.encoder(obs)
            target_latent = world_model.encoder(next_obs).detach()
            predicted_latent = world_model.predictor(current_latent, action)

            loss = torch.mean((predicted_latent - target_latent) ** 2)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            obs = next_obs

        if (episode + 1) % 20 == 0 or num_episodes <= 5:
            print(f"Épisode {episode + 1}/{num_episodes}, Perte: {total_loss / 10:.6f}")

    print("\n--- Phase 2: Planification Agentique vers un But ---")
    goal = torch.tensor([5.0, 5.0])
    current_obs = env.reset()

    viz = Visualizer(goal, output_dir=config.visualization.output_dir)
    viz.add_real_step(current_obs)

    print(f"Départ: {current_obs.tolist()}")
    print(f"Objectif: {goal.tolist()}")

    planning_steps = min(15, max(3, horizon))
    for step in range(planning_steps):
        action, imagined = planner.plan(current_obs, goal)

        imagined_2d_trajectories = []
        for traj in imagined:
            imagined_2d_trajectories.append([t[:2] for t in traj])
        viz.add_imagined_trajectories(imagined_2d_trajectories)

        if config.visualization.save_plots:
            viz.plot(f"step_{step + 1}")

        next_obs = env.step(action)
        viz.add_real_step(next_obs)

        dist = torch.norm(next_obs - goal).item()
        print(f"Étape {step + 1}: Position {next_obs.tolist()}, Distance au but: {dist:.4f}")

        current_obs = next_obs
        if dist < 0.5:
            print("But atteint !")
            break

    if config.visualization.save_plots:
        print(f"\nVisualisations générées dans {config.visualization.output_dir}.")


if __name__ == "__main__":
    main()
