from __future__ import annotations

import random
from typing import Iterable

import torch

DEFAULT_OBSTACLES: tuple[tuple[int, int], ...] = (
    (3, 3),
    (3, 4),
    (4, 3),
    (5, 5),
    (6, 5),
    (5, 6),
)


class GridWorld:
    """
    Grid-based environment with obstacles, goal, and optional transition noise.

    Preserves the SimpleEnvironment API:
    - ``reset()`` -> observation tensor
    - ``step(action)`` -> next observation tensor
    - ``transition(state, action, noise_std)`` static dynamics helper
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        noise_std: float = 0.1,
        *,
        grid_size: int = 10,
        obstacles: Iterable[tuple[int, int]] | None = None,
        goal: Iterable[float] | None = None,
        goal_tolerance: float = 0.5,
        max_steps: int = 50,
    ):
        if state_dim != 2 or action_dim != 2:
            raise ValueError("GridWorld requires state_dim=2 and action_dim=2")

        self.state_dim = state_dim
        self.action_dim = action_dim
        self.noise_std = noise_std
        self.grid_size = grid_size
        self.goal_tolerance = goal_tolerance
        self.max_steps = max_steps

        obstacle_list = list(obstacles) if obstacles is not None else list(DEFAULT_OBSTACLES)
        self.obstacles = obstacle_list
        self.obstacle_set = {
            (int(x), int(y))
            for x, y in obstacle_list
            if 0 <= int(x) < grid_size and 0 <= int(y) < grid_size
        }

        goal_values = list(goal) if goal is not None else [float(grid_size - 2), float(grid_size - 2)]
        self.goal = torch.tensor(goal_values, dtype=torch.float32)
        if self._cell_from_tensor(self.goal) in self.obstacle_set:
            raise ValueError("Goal cannot be placed on an obstacle")

        self.current_state = torch.zeros(state_dim, dtype=torch.float32)
        self._steps = 0

    def reset(self) -> torch.Tensor:
        self._steps = 0
        self.current_state = self._sample_start_position()
        return self.current_state.clone()

    def step(self, action: torch.Tensor) -> torch.Tensor:
        self._steps += 1
        self.current_state = self._apply_transition(
            self.current_state,
            action,
            noise_std=self.noise_std,
            grid_size=self.grid_size,
            obstacle_set=self.obstacle_set,
        )
        return self.current_state.clone()

    @staticmethod
    def transition(
        state: torch.Tensor,
        action: torch.Tensor,
        noise_std: float = 0.1,
        *,
        grid_size: int = 10,
        obstacles: Iterable[tuple[int, int]] | None = None,
        goal_tolerance: float = 0.5,
    ) -> torch.Tensor:
        obstacle_set = {
            (int(x), int(y))
            for x, y in (obstacles or DEFAULT_OBSTACLES)
            if 0 <= int(x) < grid_size and 0 <= int(y) < grid_size
        }
        return GridWorld._apply_transition(
            state,
            action,
            noise_std=noise_std,
            grid_size=grid_size,
            obstacle_set=obstacle_set,
        )

    def distance_to_goal(self, state: torch.Tensor | None = None) -> float:
        position = self.current_state if state is None else state
        return float(torch.norm(position - self.goal, p=2).item())

    def is_at_goal(self, state: torch.Tensor | None = None) -> bool:
        return self.distance_to_goal(state) <= self.goal_tolerance

    def _sample_start_position(self) -> torch.Tensor:
        goal_cell = self._cell_from_tensor(self.goal)
        while True:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            if (x, y) not in self.obstacle_set and (x, y) != goal_cell:
                return torch.tensor([float(x), float(y)], dtype=torch.float32)

    @staticmethod
    def _cell_from_tensor(state: torch.Tensor) -> tuple[int, int]:
        return int(round(float(state[0].item()))), int(round(float(state[1].item())))

    @classmethod
    def _apply_transition(
        cls,
        state: torch.Tensor,
        action: torch.Tensor,
        *,
        noise_std: float,
        grid_size: int,
        obstacle_set: set[tuple[int, int]],
    ) -> torch.Tensor:
        delta = action * 0.5
        if noise_std > 0:
            delta = delta + torch.randn_like(action) * noise_std

        proposed = state + delta
        proposed = torch.clamp(proposed, 0.0, float(grid_size - 1))

        cell = cls._cell_from_tensor(proposed)
        if cell in obstacle_set:
            return state.clone()
        return proposed
