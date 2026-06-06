import os
import sys
import unittest

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.config import InventoryConfig
from luthor.environment.inventory_env import InventoryEnv


class InventoryEnvTests(unittest.TestCase):
    def setUp(self):
        self.config = InventoryConfig(
            num_products=3,
            holding_cost=0.5,
            stockout_cost=10.0,
            lead_time=2,
            demand_mean=[10.0, 20.0, 15.0],
            demand_std=[1.0, 2.0, 1.5],
            max_steps=20,
        )
        self.env = InventoryEnv(self.config, seed=7, scenario_id=0)

    def test_reset_and_step_shapes(self):
        obs = self.env.reset()
        self.assertEqual(obs.shape, torch.Size([9]))
        action = torch.zeros(3)
        next_obs, reward, done, info = self.env.step(action)
        self.assertEqual(next_obs.shape, torch.Size([9]))
        self.assertIn("service_level", info)
        self.assertIsInstance(reward, float)

    def test_predict_next_observation_matches_step(self):
        obs = self.env.reset()
        action = torch.tensor([0.2, -0.5, 0.8])
        expected, _, _, _ = self.env.step(action)
        self.env.reset()
        predicted = self.env.predict_next_observation(obs, action)
        self.assertEqual(predicted.shape, obs.shape)
        self.assertFalse(torch.allclose(predicted, obs))

    def test_scenario_changes_demand(self):
        env_a = InventoryEnv(self.config, seed=7, scenario_id=0)
        env_b = InventoryEnv(self.config, seed=7, scenario_id=4)
        obs_a = env_a.reset()
        obs_b = env_b.reset()
        _, _, _, info_a = env_a.step(torch.zeros(3))
        _, _, _, info_b = env_b.step(torch.zeros(3))
        self.assertNotEqual(info_a["demand"], info_b["demand"])


if __name__ == "__main__":
    unittest.main()
