import os
import sys
import threading
import time
import unittest

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.active_learning.human_oracle import HumanLabelOracle
from luthor.active_learning.pending_labels import PendingLabelRegistry, PendingSample
from luthor.active_learning.sample import TransitionSample
from luthor.active_learning.sampler import UncertaintySampler
from luthor.config import ActiveLearningConfig
from luthor.environment.gridworld import GridWorld
from luthor.jepa_model.world_model import WorldModel


class HumanOracleTests(unittest.TestCase):
    def test_human_oracle_blocks_until_label(self):
        registry = PendingLabelRegistry()
        env = GridWorld(2, 2, noise_std=0.0, grid_size=6, obstacles=[(3, 3)], goal=[5.0, 5.0])
        oracle = HumanLabelOracle(env=env, registry=registry, timeout_seconds=5)

        obs = torch.tensor([1.0, 2.0])
        action = torch.tensor([0.5, -0.5])
        result: dict = {}

        def submit_label():
            time.sleep(0.1)
            pending = registry.list_pending()
            sample_id = pending[0]["sample_id"]
            registry.submit_label(
                sample_id,
                {"next_observation": [1.5, 1.5]},
            )

        thread = threading.Thread(target=submit_label)
        thread.start()
        next_obs = oracle.query(obs, action)
        thread.join()

        self.assertEqual(next_obs.tolist(), [1.5, 1.5])

    def test_sampler_boosts_tool_samples_when_human_in_loop(self):
        config = ActiveLearningConfig(human_in_loop=True, mc_samples=2)
        model = WorldModel(2, 2)
        sampler = UncertaintySampler(model, config)

        obs = torch.zeros(2)
        movement = TransitionSample(observation=obs, action=torch.zeros(2), sample_id="a")
        tool_use = TransitionSample(
            observation=obs,
            action={"action_type": "call_tool", "tool_name": "weather", "tool_args": {}},
            sample_id="b",
            used_tool=True,
            tool_name="weather",
        )

        movement_score = sampler.score(movement)
        tool_score = sampler.score(tool_use)
        self.assertGreater(tool_score, movement_score)


if __name__ == "__main__":
    unittest.main()
