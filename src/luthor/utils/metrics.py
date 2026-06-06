from __future__ import annotations

from dataclasses import dataclass

import torch

from luthor.environment.gridworld import GridWorld
from luthor.memory.context_compressor import ContextHistory
from luthor.training.context_session import build_context


@dataclass
class PlanningEvaluation:
    success_rate: float
    steps_per_episode: list[int]


def compute_success_rate(
    env: GridWorld,
    planner,
    num_episodes: int,
    max_steps: int | None = None,
    world_model=None,
    history_length: int = 8,
) -> PlanningEvaluation:
    """
    Compute the percentage of episodes where the agent reaches the goal in <= max_steps.
    """
    episode_limit = max_steps or env.max_steps
    successes = 0
    steps_per_episode: list[int] = []
    use_context = world_model is not None and getattr(
        world_model, "use_context_compression", False
    )

    for _ in range(num_episodes):
        observation = env.reset()
        goal = env.goal
        history = ContextHistory(history_length) if use_context else None
        if history is not None:
            history.add(observation)

        for step in range(1, episode_limit + 1):
            context = build_context(world_model, history) if history is not None else None
            if context is not None:
                action, _ = planner.plan(observation, goal, context=context)
            else:
                action, _ = planner.plan(observation, goal)
            observation = env.step(action)
            if history is not None:
                history.add(observation)
            if env.is_at_goal(observation):
                successes += 1
                steps_per_episode.append(step)
                break
        else:
            steps_per_episode.append(episode_limit)

    success_rate = (successes / num_episodes) * 100.0 if num_episodes > 0 else 0.0
    return PlanningEvaluation(success_rate=success_rate, steps_per_episode=steps_per_episode)
