import os
import sys
import unittest

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.environment.gridworld import GridWorld
from luthor.utils.metrics import compute_success_rate


class SuccessRateTests(unittest.TestCase):
    def test_compute_success_rate_all_success(self):
        env = GridWorld(2, 2, noise_std=0.0, grid_size=5, obstacles=[], goal=[4.0, 4.0], max_steps=10)

        class SuccessfulPlanner:
            def plan(self, observation, goal):
                direction = goal - observation
                action = torch.clamp(direction, -1.0, 1.0)
                return action, []

        evaluation = compute_success_rate(env, SuccessfulPlanner(), num_episodes=3, max_steps=25)
        self.assertEqual(evaluation.success_rate, 100.0)
        self.assertEqual(len(evaluation.steps_per_episode), 3)
        self.assertTrue(all(step <= 10 for step in evaluation.steps_per_episode))

    def test_compute_success_rate_none_success(self):
        env = GridWorld(2, 2, noise_std=0.0, grid_size=5, obstacles=[], goal=[4.0, 4.0], max_steps=1)

        class IdlePlanner:
            def plan(self, observation, goal):
                return torch.zeros(2), []

        evaluation = compute_success_rate(env, IdlePlanner(), num_episodes=4, max_steps=1)
        self.assertEqual(evaluation.success_rate, 0.0)
        self.assertEqual(evaluation.steps_per_episode, [1, 1, 1, 1])


if __name__ == "__main__":
    unittest.main()
