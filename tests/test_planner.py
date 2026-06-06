import os
import sys
import unittest
from unittest.mock import MagicMock

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.jepa_model.planner import Planner


class PlannerTests(unittest.TestCase):
    def test_plan_returns_action_and_trajectories(self):
        world_model = MagicMock()
        world_model.encode.side_effect = lambda obs, context=None: torch.tensor([1.0, 0.0])
        world_model.predict.side_effect = lambda state, action, context=None: state + 0.1

        def cost_fn(state, goal):
            return float(torch.sum((state - goal) ** 2))

        planner = Planner(
            world_model=world_model,
            action_dim=2,
            horizon=3,
            num_samples=5,
            cost_function=cost_fn,
        )

        action, trajectories = planner.plan(
            current_observation=torch.zeros(2),
            goal_observation=torch.ones(2),
        )

        self.assertEqual(action.shape, (2,))
        self.assertEqual(len(trajectories), 5)
        self.assertEqual(len(trajectories[0]), 4)  # horizon + initial state


if __name__ == "__main__":
    unittest.main()
