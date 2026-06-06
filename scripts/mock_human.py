#!/usr/bin/env python3
"""Simulated human labeler for demo mode (polls /label/pending, posts /label)."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import httpx
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from luthor.active_learning.oracle import DummyOracle
from luthor.environment.gridworld import GridWorld, is_tool_action


def build_outcome(observation: list[float], action, oracle: DummyOracle) -> dict:
    obs = torch.tensor(observation, dtype=torch.float32)
    if isinstance(action, list):
        tensor_action = torch.tensor(action, dtype=torch.float32)
    else:
        tensor_action = action

    next_obs = oracle.query(obs, tensor_action)
    outcome = {"next_observation": next_obs.tolist()}

    if isinstance(action, dict) and is_tool_action(action) and action.get("tool_name") == "weather":
        outcome["weather_relevant"] = True

    return outcome


def main() -> None:
    parser = argparse.ArgumentParser(description="Mock human labeler for Luthor active learning")
    parser.add_argument("--api-url", default="http://localhost:8080")
    parser.add_argument("--poll-interval", type=float, default=1.0)
    parser.add_argument("--once", action="store_true", help="Process pending labels once and exit")
    args = parser.parse_args()

    env = GridWorld(2, 2, noise_std=0.0, weather_enabled=True)
    oracle = DummyOracle(env=env)

    with httpx.Client(base_url=args.api_url, timeout=30.0) as client:
        while True:
            response = client.get("/label/pending")
            response.raise_for_status()
            pending = response.json().get("pending", [])

            for sample in pending:
                outcome = build_outcome(sample["observation"], sample["action"], oracle)
                label_response = client.post(
                    "/label",
                    json={
                        "sample_id": sample["sample_id"],
                        "correct_outcome": outcome,
                    },
                )
                label_response.raise_for_status()
                print(f"Labeled sample_id={sample['sample_id']}")

            if args.once and not pending:
                break
            if args.once and pending:
                args.once = False

            time.sleep(args.poll_interval)


if __name__ == "__main__":
    main()
