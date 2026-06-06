import os
import sys
import unittest

import torch
import torch.nn as nn

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.config import EncoderConfig, MemoryConfig, PredictorConfig
from luthor.jepa_model.world_model import WorldModel
from luthor.training.context_session import jepa_train_step_with_context


class SubquadraticPredictorTests(unittest.TestCase):
    def _build_world_model(self) -> WorldModel:
        return WorldModel(
            input_dim=2,
            action_dim=2,
            encoder_config=EncoderConfig(latent_dim=8, hidden_dim=16, num_layers=2),
            predictor_config=PredictorConfig(
                predictor_type="linear_attention",
                hidden_dim=16,
                num_layers=2,
                linear_attention_dim_head=8,
                linear_attention_heads=2,
                feature_map="elu+1",
            ),
            memory_config=MemoryConfig(use_context_compression=True, history_length=5),
            latent_dim=8,
        )

    def test_world_model_uses_subquadratic_predictor(self):
        from luthor.jepa_model.linear_attention import SubquadraticPredictor

        world_model = self._build_world_model()
        self.assertIsInstance(world_model.predictor, SubquadraticPredictor)

    def test_forward_with_sequence_context(self):
        world_model = self._build_world_model()
        world_model.eval()

        latent = torch.randn(8)
        action = torch.randn(2)
        history = torch.randn(12, 8)
        output = world_model.predict(latent, action, context=history)
        self.assertEqual(output.shape, torch.Size([8]))

    def test_loss_can_decrease_over_steps(self):
        world_model = self._build_world_model()
        optimizer = torch.optim.Adam(world_model.parameters(), lr=0.05)
        criterion = nn.MSELoss()

        obs = torch.tensor([0.2, 0.3])
        action = torch.tensor([0.1, -0.1])
        next_obs = torch.tensor([0.4, 0.2])
        context = torch.randn(8)

        losses: list[float] = []
        for _ in range(12):
            loss = jepa_train_step_with_context(
                world_model,
                optimizer,
                obs,
                action,
                next_obs,
                context=context,
            )
            losses.append(loss)

        self.assertLess(losses[-1], losses[0])


if __name__ == "__main__":
    unittest.main()
