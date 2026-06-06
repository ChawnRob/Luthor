from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from luthor.pipeline.params import load_params


def build_gridworld_spec(params: dict) -> dict:
    gridworld = dict(params["gridworld"])
    gridworld["version"] = params.get("version", "1")
    gridworld["seed"] = params.get("seed", 42)
    gridworld["generated_at"] = datetime.now(timezone.utc).isoformat()
    return gridworld


def prepare_data(params_path: str | Path, output_path: str | Path) -> Path:
    params = load_params(params_path)
    spec = build_gridworld_spec(params)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(spec, handle, indent=2)
        handle.write("\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a versioned GridWorld spec for DVC.")
    parser.add_argument("params", help="Path to params.yaml")
    parser.add_argument("output", help="Output path, e.g. data/raw/gridworld.json")
    args = parser.parse_args()
    output = prepare_data(args.params, args.output)
    print(f"GridWorld spec written to {output}")


if __name__ == "__main__":
    main()
