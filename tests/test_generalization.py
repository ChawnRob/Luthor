import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.config import (
    ABTestingConfig,
    ActiveLearningConfig,
    EncoderConfig,
    EnvironmentConfig,
    GeneralizationConfig,
    GridWorldConfig,
    InventoryConfig,
    LoggingConfig,
    LuthorConfig,
    MemoryConfig,
    PlannerConfig,
    PredictorConfig,
    VisualizationConfig,
)
from luthor.jepa_model.world_model import WorldModel
from luthor.utils.generalization import compute_generalization_success


def _inventory_config() -> LuthorConfig:
    inventory = InventoryConfig(
        num_products=2,
        demand_mean=[5.0, 8.0],
        demand_std=[1.0, 1.0],
        max_steps=10,
        service_level_target=0.5,
    )
    return LuthorConfig(
        encoder=EncoderConfig(latent_dim=4, hidden_dim=8, num_layers=1),
        predictor=PredictorConfig(hidden_dim=8, num_layers=1, use_attention=True),
        planner=PlannerConfig(horizon=2, num_samples=2, learning_rate=0.01, num_iterations=2),
        visualization=VisualizationConfig(enabled=False),
        logging=LoggingConfig(),
        active_learning=ActiveLearningConfig(input_dim=6, action_dim=2),
        memory=MemoryConfig(use_context_compression=False),
        ab_testing=ABTestingConfig(),
        environment=EnvironmentConfig(type="inventory", inventory=inventory),
        gridworld=GridWorldConfig(),
        generalization=GeneralizationConfig(
            train_scenarios=[0, 1],
            test_scenarios=[4, 5],
            max_steps=8,
        ),
        seed=3,
    )


class GeneralizationTests(unittest.TestCase):
    def test_generalization_success_returns_score(self):
        config = _inventory_config()
        world_model = WorldModel(
            6,
            2,
            encoder_config=config.encoder,
            predictor_config=config.predictor,
            memory_config=config.memory,
            latent_dim=4,
        )
        evaluation = compute_generalization_success(config, world_model)
        self.assertGreaterEqual(evaluation.generalization_success, 0.0)
        self.assertLessEqual(evaluation.generalization_success, 100.0)
        self.assertEqual(set(evaluation.scenario_results.keys()), {4, 5})


if __name__ == "__main__":
    unittest.main()
