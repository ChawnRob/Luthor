#!/usr/bin/env python3
"""Optional mock human labeler (polls /label/pending, posts /label)."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import httpx
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from luthor.active_learning.oracle import DummyOracle
from luthor.config import InventoryConfig, LuthorConfig
from luthor.environment.factory import build_environment


def build_oracle_env(config: LuthorConfig):
    return build_environment(config, seed=config.seed)


def main() -> None:
    parser = argparse.ArgumentParser(description="Mock human labeler for Luthor")
    parser.add_argument("--api-url", default="http://localhost:8080")
    parser.add_argument("--poll-interval", type=float, default=1.0)
    args = parser.parse_args()

    from luthor.config import get_config

    config = get_config()
    env = build_oracle_env(config)
    oracle = DummyOracle(env=env)

    with httpx.Client(base_url=args.api_url, timeout=30.0) as client:
        while True:
            response = client.get("/label/pending")
            response.raise_for_status()
            for sample in response.json().get("pending", []):
                obs = torch.tensor(sample["observation"], dtype=torch.float32)
                action = torch.tensor(sample["action"], dtype=torch.float32)
                next_obs = oracle.query(obs, action)
                client.post(
                    "/label",
                    json={
                        "sample_id": sample["sample_id"],
                        "correct_outcome": {"next_observation": next_obs.tolist()},
                    },
                ).raise_for_status()
                print(f"Labeled {sample['sample_id']}")
            time.sleep(args.poll_interval)


if __name__ == "__main__":
    main()
