import os

import matplotlib

matplotlib.use("Agg")

import torch
import torch.optim as optim

from luthor.config import get_config
from luthor.environment.gridworld import GridWorld
from luthor.jepa_model.planner import Planner
from luthor.jepa_model.world_model import WorldModel
from luthor.utils.cost_function import euclidean_distance_cost
from luthor.utils.logging import build_run_log, write_run_log
from luthor.utils.metrics import compute_success_rate
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
    eval_episodes = int(os.getenv("LUTHOR_EVAL_EPISODES", "5"))

    os.makedirs(config.visualization.output_dir, exist_ok=True)

    env = GridWorld(input_dim, action_dim, noise_std=0.1)
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
    final_loss = 0.0
    for episode in range(num_episodes):
        obs = env.reset()
        total_loss = 0.0
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

        final_loss = total_loss / 10
        if (episode + 1) % 20 == 0 or num_episodes <= 5:
            print(f"Épisode {episode + 1}/{num_episodes}, Perte: {final_loss:.6f}")

    print("\n--- Phase 2: Planification Agentique vers un But ---")
    goal = env.goal.clone()
    current_obs = env.reset()

    viz = Visualizer(goal, output_dir=config.visualization.output_dir)
    viz.add_real_step(current_obs)

    print(f"Départ: {current_obs.tolist()}")
    print(f"Objectif: {goal.tolist()}")

    planning_steps = min(env.max_steps, max(3, horizon))
    demo_steps_per_episode: list[int] = []
    for step in range(1, planning_steps + 1):
        action, imagined = planner.plan(current_obs, goal)

        imagined_2d_trajectories = []
        for traj in imagined:
            imagined_2d_trajectories.append([t[:2] for t in traj])
        viz.add_imagined_trajectories(imagined_2d_trajectories)

        if config.visualization.save_plots:
            viz.plot(f"step_{step}")

        next_obs = env.step(action)
        viz.add_real_step(next_obs)

        dist = env.distance_to_goal(next_obs)
        print(f"Étape {step}: Position {next_obs.tolist()}, Distance au but: {dist:.4f}")

        current_obs = next_obs
        if env.is_at_goal(next_obs):
            print("But atteint !")
            demo_steps_per_episode.append(step)
            break
    else:
        demo_steps_per_episode.append(planning_steps)

    print("\n--- Phase 3: Évaluation (success_rate) ---")
    evaluation = compute_success_rate(env, planner, num_episodes=eval_episodes, max_steps=env.max_steps)
    print(f"success_rate={evaluation.success_rate:.2f}%")

    hyperparameters = {
        "latent_dim": latent_dim,
        "horizon": horizon,
        "num_samples": num_samples,
        "learning_rate": learning_rate,
        "num_episodes": num_episodes,
        "eval_episodes": eval_episodes,
        "grid_size": env.grid_size,
        "max_steps": env.max_steps,
        "noise_std": env.noise_std,
        "goal": goal.tolist(),
    }
    log_payload = build_run_log(
        run_type="demo",
        hyperparameters=hyperparameters,
        final_loss=final_loss,
        success_rate=evaluation.success_rate,
        steps_per_episode=evaluation.steps_per_episode,
    )
    log_path = write_run_log(
        os.path.join(config.visualization.output_dir, "demo_run.json"),
        log_payload,
    )
    print(f"Run log écrit dans {log_path}")

    if config.visualization.save_plots:
        print(f"Visualisations générées dans {config.visualization.output_dir}.")


if __name__ == "__main__":
    main()
