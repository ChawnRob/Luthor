import os
import sys
import unittest

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.config import EncoderConfig, MemoryConfig, PredictorConfig
from luthor.jepa_model.world_model import WorldModel
from luthor.memory.context_compressor import ContextHistory
from luthor.training.context_session import build_context, jepa_train_step_with_context


class ContextIntegrationTests(unittest.TestCase):
    def _build_world_model(self, use_context: bool) -> WorldModel:
        return WorldModel(
            input_dim=2,
            action_dim=2,
            encoder_config=EncoderConfig(latent_dim=8, hidden_dim=16, num_layers=2),
            predictor_config=PredictorConfig(hidden_dim=16, num_layers=2, use_attention=True),
            memory_config=MemoryConfig(
                use_context_compression=use_context,
                history_length=5,
                gru_hidden_dim=16,
                gru_num_layers=1,
            ),
            latent_dim=8,
        )

    def test_context_changes_prediction(self):
        world_model = self._build_world_model(use_context=True)
        world_model.eval()

        observation = torch.tensor([1.0, 2.0])
        action = torch.tensor([0.3, -0.2])
        latent = world_model.encode(observation, context=None)

        without_context = world_model.predict(latent, action, context=None)

        history = ContextHistory(max_length=5)
        history.add(torch.tensor([0.0, 0.0]))
        history.add(torch.tensor([1.0, 1.0]))
        history.add(torch.tensor([2.0, 2.0]))
        context = build_context(world_model, history)
        self.assertIsNotNone(context)

        with_context = world_model.predict(latent, action, context=context)
        self.assertFalse(torch.allclose(without_context, with_context, atol=1e-6))

    def test_target_encoding_ignores_context(self):
        world_model = self._build_world_model(use_context=True)
        next_obs = torch.tensor([2.0, 3.0])
        context = torch.ones(8)

        target_without = world_model.encode_target(next_obs)
        contextual_encoder_output = world_model.encode(next_obs, context=context)
        self.assertFalse(torch.allclose(target_without, contextual_encoder_output, atol=1e-6))
        self.assertEqual(target_without.shape, torch.Size([8]))

    def test_end_to_end_training_step_runs_with_context(self):
        world_model = self._build_world_model(use_context=True)
        optimizer = torch.optim.Adam(world_model.parameters(), lr=0.01)

        obs = torch.tensor([0.5, 0.5])
        action = torch.tensor([0.1, -0.1])
        next_obs = torch.tensor([0.7, 0.4])
        context = torch.zeros(8)

        loss = jepa_train_step_with_context(
            world_model,
            optimizer,
            obs,
            action,
            next_obs,
            context=context,
        )
        self.assertGreaterEqual(loss, 0.0)


if __name__ == "__main__":
    unittest.main()
