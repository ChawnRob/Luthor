from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def _prompts_dir() -> Path:
    override = os.getenv("LUTHOR_PROMPTS_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[3] / "prompts"


def list_prompts() -> list[dict[str, Any]]:
    directory = _prompts_dir()
    prompts: list[dict[str, Any]] = []
    if not directory.exists():
        return prompts

    for path in sorted(directory.glob("*.txt")):
        prompts.append(
            {
                "name": path.name,
                "version": _version_from_filename(path.name),
                "content": path.read_text(encoding="utf-8"),
            }
        )
    return prompts


def load_system_prompt(version: str) -> str:
    directory = _prompts_dir()
    filename = f"system_{version}.txt"
    path = directory / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def _version_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    if stem.startswith("system_"):
        return stem.removeprefix("system_")
    return stem
