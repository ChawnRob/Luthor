import os

import matplotlib

matplotlib.use("Agg")

from luthor.active_learning.loop import ActiveLearningLoop
from luthor.config import get_config
from luthor.environment.gridworld import GridWorld
from luthor.jepa_model.planner import Planner
from luthor.utils.cost_function import euclidean_distance_cost
from luthor.utils.logging import build_run_log, write_run_log
from luthor.utils.metrics import compute_success_rate


def main():
    config = get_config()
    os.makedirs(config.visualization.output_dir, exist_ok=True)
    eval_episodes = int(os.getenv("LUTHOR_EVAL_EPISODES", "5"))

    print("--- Luthor Active Learning (JEPA SLM skeleton) ---")
    oracle_mode = (
        "human-in-the-loop (/label)"
        if config.active_learning.human_in_loop
        else "dummy oracle"
    )
    print(
        f"Uncertainty sampling via predictor variance + {oracle_mode} "
        f"({config.active_learning.num_rounds} rounds)"
    )
    if config.tools.weather.enabled:
        print("Weather tool enabled (call_tool actions in pool)")
    if config.memory.use_context_compression:
        print(f"Context compression enabled (history={config.memory.history_length})")

    env = GridWorld(
        config.active_learning.input_dim,
        config.active_learning.action_dim,
        noise_std=0.0,
    )
    loop = ActiveLearningLoop(config, env=env)
    results = loop.run()

    final_loss = results[-1].mean_loss if results else 0.0
    print(f"\nActive learning complete. Final mean loss: {final_loss:.6f}")

    print("\n--- Évaluation planification (success_rate) ---")
    planner = Planner(
        loop.world_model,
        config.active_learning.action_dim,
        config.planner.horizon,
        config.planner.num_samples,
        euclidean_distance_cost,
    )
    evaluation = compute_success_rate(
        env,
        planner,
        num_episodes=eval_episodes,
        max_steps=env.max_steps,
        world_model=loop.world_model,
        history_length=config.memory.history_length,
    )
    print(f"success_rate={evaluation.success_rate:.2f}%")

    hyperparameters = {
        "num_rounds": config.active_learning.num_rounds,
        "pool_size": config.active_learning.pool_size,
        "query_batch_size": config.active_learning.query_batch_size,
        "mc_samples": config.active_learning.mc_samples,
        "train_steps_per_round": config.active_learning.train_steps_per_round,
        "learning_rate": config.planner.learning_rate,
        "eval_episodes": eval_episodes,
        "grid_size": env.grid_size,
        "max_steps": env.max_steps,
        "goal": env.goal.tolist(),
        "use_context_compression": config.memory.use_context_compression,
        "history_length": config.memory.history_length,
    }
    log_payload = build_run_log(
        run_type="active_demo",
        hyperparameters=hyperparameters,
        final_loss=final_loss,
        success_rate=evaluation.success_rate,
        steps_per_episode=evaluation.steps_per_episode,
        extra={"active_learning_rounds": [result.__dict__ for result in results]},
    )
    log_path = write_run_log(
        os.path.join(config.visualization.output_dir, "active_demo_run.json"),
        log_payload,
    )
    print(f"Run log écrit dans {log_path}")


if __name__ == "__main__":
    main()
