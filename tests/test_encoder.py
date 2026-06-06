import os
import sys
import unittest

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.config import EncoderConfig
from luthor.jepa_model.encoder import Encoder


class EncoderTests(unittest.TestCase):
    def test_forward_produces_latent_vector(self):
        config = EncoderConfig(latent_dim=8, hidden_dim=16, num_layers=2, dropout=0.0)
        encoder = Encoder(input_dim=4, encoder_config=config)
        observation = torch.randn(4)
        latent = encoder(observation)
        self.assertEqual(latent.shape, (8,))

    def test_batch_observation_shape(self):
        config = EncoderConfig(latent_dim=4, hidden_dim=8, num_layers=1, dropout=0.0)
        encoder = Encoder(input_dim=2, encoder_config=config)
        batch = torch.randn(3, 2)
        latent = encoder(batch)
        self.assertEqual(latent.shape, (3, 4))


if __name__ == "__main__":
    unittest.main()
