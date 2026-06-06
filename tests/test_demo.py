import os
import sys
import tempfile
import unittest
from io import StringIO
from unittest import mock

# Ensure src is on the path when running tests from the repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class LuthorPackageTests(unittest.TestCase):
    def setUp(self):
        os.environ["LUTHOR_ENCODER_LATENT_DIM"] = "4"
        os.environ["LUTHOR_ENCODER_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_ENCODER_NUM_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_PREDICTOR_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_USE_ATTENTION"] = "true"
        os.environ["LUTHOR_PLANNER_HORIZON"] = "3"
        os.environ["LUTHOR_PLANNER_NUM_SAMPLES"] = "5"
        os.environ["LUTHOR_PLANNER_LR"] = "0.01"
        os.environ["LUTHOR_PLANNER_ITERATIONS"] = "2"
        os.environ["LUTHOR_VISUALIZATION_SAVE_PLOTS"] = "true"

        from luthor.config import reset_config

        reset_config()

    def tearDown(self):
        from luthor.config import reset_config

        reset_config()

    def test_package_imports(self):
        import luthor

        self.assertEqual(luthor.Predictor.__name__, "Predictor")
        self.assertEqual(luthor.Planner.__name__, "Planner")
        self.assertTrue(callable(luthor.CostFunction.euclidean))

    def test_jepa_model_uses_config(self):
        from luthor.config import EncoderConfig, PredictorConfig, get_config
        from luthor.jepa_model.world_model import WorldModel

        config = get_config()
        model = WorldModel(
            input_dim=2,
            action_dim=2,
            encoder_config=config.encoder,
            predictor_config=config.predictor,
        )

        self.assertEqual(model.encoder.latent_dim, 4)
        self.assertTrue(model.predictor.use_attention)

        config.predictor.use_attention = False
        model_without_attention = WorldModel(
            input_dim=2,
            action_dim=2,
            encoder_config=EncoderConfig(latent_dim=8, hidden_dim=16, num_layers=2),
            predictor_config=config.predictor,
        )
        self.assertFalse(model_without_attention.predictor.use_attention)

    def test_demo_runs_without_errors(self):
        from luthor.config import reset_config
        from luthor import demo

        reset_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["LUTHOR_VISUALIZATION_OUTPUT_DIR"] = tmpdir
            reset_config()

            stdout = StringIO()
            with mock.patch("sys.stdout", stdout):
                demo.main()

            output = stdout.getvalue()
            self.assertIn("Phase 1", output)
            self.assertIn("Phase 2", output)
            self.assertTrue(any(name.startswith("luthor_step_") for name in os.listdir(tmpdir)))


if __name__ == "__main__":
    unittest.main()
