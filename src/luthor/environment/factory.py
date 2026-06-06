from __future__ import annotations

from luthor.config import LuthorConfig
from luthor.environment.gridworld import DEFAULT_OBSTACLES, GridWorld
from luthor.environment.inventory_env import InventoryEnv


def build_environment(config: LuthorConfig, *, seed: int | None = None, scenario_id: int = 0):
    env_type = config.environment.type
    if env_type == "inventory":
        return InventoryEnv.from_config(
            config.environment.inventory,
            seed=seed,
            scenario_id=scenario_id,
        )

    grid = config.gridworld
    obstacles = [tuple(cell) for cell in grid.obstacles] if grid.obstacles else list(DEFAULT_OBSTACLES)
    return GridWorld(
        grid.state_dim,
        grid.action_dim,
        noise_std=grid.noise_std,
        grid_size=grid.grid_size,
        obstacles=obstacles,
        goal=grid.goal,
        goal_tolerance=grid.goal_tolerance,
        max_steps=grid.max_steps,
    )


def environment_dims(config: LuthorConfig) -> tuple[int, int]:
    env = build_environment(config)
    return env.state_dim, env.action_dim
