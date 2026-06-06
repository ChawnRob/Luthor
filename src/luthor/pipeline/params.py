from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from luthor.config import LuthorConfig


def load_params(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def config_from_params(params: dict[str, Any]) -> LuthorConfig:
    return LuthorConfig.from_params(params)
