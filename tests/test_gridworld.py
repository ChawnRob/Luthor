import os
import sys
import unittest

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.environment.gridworld import GridWorld
from luthor.environment.simple_env import SimpleEnvironment


class GridWorldTests(unittest.TestCase):
    def setUp(self):
        self.env = GridWorld(
            2,
            2,
            noise_std=0.0,
            grid_size=6,
            obstacles=[(2, 2)],
            goal=[5.0, 5.0],
            max_steps=20,
        )

    def test_simple_environment_alias(self):
        self.assertIs(SimpleEnvironment, GridWorld)

    def test_reset_returns_valid_free_cell(self):
        state = self.env.reset()
        self.assertEqual(state.shape, torch.Size([2]))
        cell = GridWorld._cell_from_tensor(state)
        self.assertNotIn(cell, self.env.obstacle_set)
        self.assertNotEqual(cell, GridWorld._cell_from_tensor(self.env.goal))

    def test_step_moves_agent_without_noise(self):
        self.env.current_state = torch.tensor([1.0, 1.0])
        next_state = self.env.step(torch.tensor([1.0, 0.0]))
        self.assertGreater(next_state[0].item(), 1.0)

    def test_obstacle_blocks_movement(self):
        self.env.current_state = torch.tensor([1.0, 2.0])
        blocked = self.env.step(torch.tensor([1.0, 0.0]))
        self.assertEqual(blocked.tolist(), [1.0, 2.0])

    def test_is_at_goal(self):
        self.assertTrue(self.env.is_at_goal(torch.tensor([5.0, 5.0])))
        self.assertFalse(self.env.is_at_goal(torch.tensor([0.0, 0.0])))

    def test_static_transition_matches_env_dynamics(self):
        state = torch.tensor([1.0, 1.0])
        action = torch.tensor([1.0, 0.0])
        expected = GridWorld._apply_transition(
            state,
            action,
            noise_std=0.0,
            grid_size=self.env.grid_size,
            obstacle_set=self.env.obstacle_set,
        )
        actual = GridWorld.transition(
            state,
            action,
            noise_std=0.0,
            grid_size=self.env.grid_size,
            obstacles=self.env.obstacles,
        )
        self.assertEqual(expected.tolist(), actual.tolist())


if __name__ == "__main__":
    unittest.main()
