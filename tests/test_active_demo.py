import os
import sys
import unittest
from io import StringIO
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class ActiveLearningTests(unittest.TestCase):
    def setUp(self):
        os.environ["LUTHOR_ENCODER_LATENT_DIM"] = "4"
        os.environ["LUTHOR_ENCODER_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_ENCODER_NUM_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_PREDICTOR_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_USE_ATTENTION"] = "true"
        os.environ["LUTHOR_PLANNER_LR"] = "0.01"
        os.environ["LUTHOR_AL_ROUNDS"] = "2"
        os.environ["LUTHOR_AL_POOL_SIZE"] = "8"
        os.environ["LUTHOR_AL_QUERY_BATCH"] = "3"
        os.environ["LUTHOR_AL_MC_SAMPLES"] = "3"
        os.environ["LUTHOR_AL_TRAIN_STEPS"] = "2"
        os.environ["LUTHOR_WEATHER_ENABLED"] = "false"
        os.environ["LUTHOR_VISUALIZATION_OUTPUT_DIR"] = "/tmp/luthor-test-outputs"

        from luthor.config import reset_config

        reset_config()

    def tearDown(self):
        from luthor.config import reset_config

        reset_config()

    def test_uncertainty_sampler_ranks_candidates(self):
        import torch

        from luthor.active_learning.sampler import UncertaintySampler
        from luthor.config import get_config
        from luthor.jepa_model.world_model import WorldModel

        config = get_config()
        model = WorldModel(2, 2, encoder_config=config.encoder, predictor_config=config.predictor)
        sampler = UncertaintySampler(model, config.active_learning)

        from luthor.active_learning.sample import TransitionSample

        pool = [
            TransitionSample(torch.zeros(2), torch.ones(2), sample_id="a"),
            TransitionSample(torch.ones(2), torch.zeros(2), sample_id="b"),
        ]
        selected = sampler.select(pool, query_batch_size=1)
        self.assertEqual(len(selected), 1)

    def test_dummy_oracle_returns_next_state(self):
        import torch

        from luthor.active_learning.oracle import DummyOracle
        from luthor.environment.gridworld import GridWorld

        env = GridWorld(2, 2, noise_std=0.0, grid_size=6, obstacles=[(3, 3)], goal=[5.0, 5.0])
        oracle = DummyOracle(env=env)
        obs = torch.tensor([1.0, 2.0])
        action = torch.tensor([0.5, -0.5])
        next_obs = oracle.query(obs, action)
        self.assertEqual(next_obs.shape, obs.shape)

    def test_active_demo_runs_without_errors(self):
        from luthor import active_demo
        from luthor.config import reset_config

        reset_config()

        stdout = StringIO()
        with mock.patch("sys.stdout", stdout):
            active_demo.main()

        output = stdout.getvalue()
        self.assertIn("Active Learning", output)
        self.assertIn("Active learning complete", output)
        self.assertIn("success_rate", output)
        self.assertTrue(os.path.exists(os.path.join("/tmp/luthor-test-outputs", "active_demo_run.json")))


if __name__ == "__main__":
    unittest.main()
