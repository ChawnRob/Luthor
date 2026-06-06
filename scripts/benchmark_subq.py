#!/usr/bin/env python3
"""Benchmark MLP vs linear-attention predictors on long context sequences."""

from __future__ import annotations

import argparse
import sys
import time
import tracemalloc
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from luthor.config import EncoderConfig, MemoryConfig, PredictorConfig
from luthor.jepa_model.world_model import WorldModel


def _build_model(predictor_type: str, hidden_dim: int, context_dim: int) -> WorldModel:
    return WorldModel(
        input_dim=context_dim,
        action_dim=2,
        encoder_config=EncoderConfig(latent_dim=16, hidden_dim=hidden_dim, num_layers=2),
        predictor_config=PredictorConfig(
            predictor_type=predictor_type,
            hidden_dim=hidden_dim,
            num_layers=2,
            use_attention=True,
            linear_attention_dim_head=16,
            linear_attention_heads=4,
            feature_map="elu+1",
        ),
        memory_config=MemoryConfig(use_context_compression=True, history_length=8),
        latent_dim=16,
    )


def _run_forward(
    model: WorldModel,
    seq_len: int,
    context_dim: int,
    *,
    warmup: int,
    repeats: int,
) -> tuple[float, int]:
    model.eval()
    latent = torch.randn(16)
    action = torch.randn(2)
    history = torch.randn(seq_len, context_dim)

    with torch.no_grad():
        for _ in range(warmup):
            model.predict(latent, action, context=history)

    if torch.cuda.is_available():
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()

    tracemalloc.start()
    start = time.perf_counter()
    with torch.no_grad():
        for _ in range(repeats):
            model.predict(latent, action, context=history)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    elapsed = (time.perf_counter() - start) / repeats
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if torch.cuda.is_available():
        peak = max(peak, torch.cuda.max_memory_allocated())

    return elapsed, peak


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark subquadratic predictor scaling")
    parser.add_argument("--seq-lengths", nargs="+", type=int, default=[10, 50, 200])
    parser.add_argument("--hidden-dim", type=int, default=64)
    parser.add_argument("--context-dim", type=int, default=16)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=10)
    args = parser.parse_args()

    results: list[dict] = []
    for seq_len in args.seq_lengths:
        row = {"seq_len": seq_len}
        for predictor_type in ("mlp", "linear_attention"):
            model = _build_model(predictor_type, args.hidden_dim, args.context_dim)
            elapsed, peak = _run_forward(
                model,
                seq_len,
                args.context_dim,
                warmup=args.warmup,
                repeats=args.repeats,
            )
            row[f"{predictor_type}_seconds"] = elapsed
            row[f"{predictor_type}_peak_bytes"] = peak
        row["speedup"] = row["mlp_seconds"] / max(row["linear_attention_seconds"], 1e-9)
        row["memory_ratio"] = row["mlp_peak_bytes"] / max(row["linear_attention_peak_bytes"], 1)
        results.append(row)

    print("seq_len | mlp_s | linear_s | speedup | memory_ratio")
    for row in results:
        print(
            f"{row['seq_len']:>7} | "
            f"{row['mlp_seconds']:.6f} | "
            f"{row['linear_attention_seconds']:.6f} | "
            f"{row['speedup']:.2f}x | "
            f"{row['memory_ratio']:.2f}x"
        )


if __name__ == "__main__":
    main()
