#!/usr/bin/env python3
"""Run the LUTHOR full MCP demo workflow from the command line."""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from luthor.demo_workflow import (  # noqa: E402
    DEFAULT_DEMO_MESSAGE,
    default_output_dir,
    run_demo_workflow,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="LUTHOR full MCP demo workflow")
    parser.add_argument(
        "--message",
        default=DEFAULT_DEMO_MESSAGE,
        help="User request for the Mistral orchestrator",
    )
    parser.add_argument(
        "--output-dir",
        default=str(default_output_dir()),
        help="Directory for demo artifacts (default: demo_outputs/)",
    )
    args = parser.parse_args()

    try:
        asyncio.run(
            run_demo_workflow(
                args.message,
                output_dir=Path(args.output_dir),
            )
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Demo failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
