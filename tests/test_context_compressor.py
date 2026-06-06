import os
import sys
import unittest

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.memory.context_compressor import ContextCompressor, ContextHistory


class ContextCompressorTests(unittest.TestCase):
    def test_compress_output_shape(self):
        compressor = ContextCompressor(input_dim=2, latent_dim=4, hidden_dim=16, num_layers=1)
        sequence = torch.randn(6, 2)
        context = compressor.compress(sequence)
        self.assertEqual(context.shape, torch.Size([4]))

    def test_compress_batch_output_shape(self):
        compressor = ContextCompressor(input_dim=2, latent_dim=4, hidden_dim=16, num_layers=1)
        sequence = torch.randn(2, 6, 2)
        context = compressor.compress(sequence)
        self.assertEqual(context.shape, torch.Size([2, 4]))

    def test_compress_supports_gradients(self):
        compressor = ContextCompressor(input_dim=2, latent_dim=4, hidden_dim=8, num_layers=1)
        sequence = torch.randn(5, 2, requires_grad=True)
        context = compressor.compress(sequence)
        loss = context.pow(2).mean()
        loss.backward()
        self.assertIsNotNone(sequence.grad)
        self.assertGreater(float(sequence.grad.abs().sum()), 0.0)

    def test_context_history_rolling_window(self):
        history = ContextHistory(max_length=3)
        for value in [1.0, 2.0, 3.0, 4.0]:
            history.add(torch.tensor([value, value]))
        sequence = history.as_sequence()
        self.assertIsNotNone(sequence)
        assert sequence is not None
        self.assertEqual(sequence.shape[0], 3)
        self.assertEqual(float(sequence[-1][0]), 4.0)


if __name__ == "__main__":
    unittest.main()
