import os
import sys
import time
import unittest

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.jepa_model.linear_attention import LinearAttention


class LinearAttentionTests(unittest.TestCase):
    def test_output_shape_and_gradients(self):
        attention = LinearAttention(dim=32, num_heads=4, feature_map="elu+1")
        query = torch.randn(2, 5, 32, requires_grad=True)
        key = torch.randn(2, 7, 32, requires_grad=True)
        value = torch.randn(2, 7, 32, requires_grad=True)

        output = attention(query, key, value)
        self.assertEqual(output.shape, (2, 5, 32))
        loss = output.sum()
        loss.backward()
        self.assertIsNotNone(query.grad)
        self.assertIsNotNone(key.grad)
        self.assertIsNotNone(value.grad)

    def test_feature_maps(self):
        for feature_map in ("elu+1", "relu"):
            module = LinearAttention(dim=16, num_heads=2, feature_map=feature_map)
            output = module(
                torch.randn(1, 3, 16),
                torch.randn(1, 4, 16),
                torch.randn(1, 4, 16),
            )
            self.assertEqual(output.shape, (1, 3, 16))

    def test_scaling_is_subquadratic(self):
        torch.manual_seed(0)
        standard = torch.nn.MultiheadAttention(embed_dim=32, num_heads=4, batch_first=True)
        linear = LinearAttention(dim=32, num_heads=4)

        def time_attention(seq_len: int, repeats: int = 40) -> tuple[float, float]:
            tokens = torch.randn(1, seq_len, 32)
            query = tokens[:, :1, :]

            start = time.perf_counter()
            with torch.no_grad():
                for _ in range(repeats):
                    standard(query, tokens, tokens)
            standard_elapsed = time.perf_counter() - start

            start = time.perf_counter()
            with torch.no_grad():
                for _ in range(repeats):
                    linear(query, tokens, tokens)
            linear_elapsed = time.perf_counter() - start
            return standard_elapsed, linear_elapsed

        std_short, lin_short = time_attention(16, repeats=60)
        std_long, lin_long = time_attention(96, repeats=60)

        std_growth = std_long / max(std_short, 1e-9)
        lin_growth = lin_long / max(lin_short, 1e-9)
        self.assertGreater(std_growth, lin_growth)
        self.assertGreater(std_growth / max(lin_growth, 1e-9), 1.05)


if __name__ == "__main__":
    unittest.main()
