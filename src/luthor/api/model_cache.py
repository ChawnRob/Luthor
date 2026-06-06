from __future__ import annotations

from pathlib import Path

import torch

from luthor.config import ABTestingConfig, LuthorConfig
from luthor.jepa_model.world_model import WorldModel

ALLOWED_VERSIONS = frozenset({"default", "candidate"})


class ModelCache:
    """Cache JEPA world models for A/B testing."""

    def __init__(self, config: LuthorConfig):
        self.config = config
        self._models: dict[str, WorldModel] = {}

    def resolve_version(self, requested: str | None) -> str:
        if not self.config.ab_testing.enabled:
            return "default"
        if requested in ALLOWED_VERSIONS:
            return requested
        return "default"

    def get_world_model(self, version: str | None = None) -> tuple[WorldModel, str]:
        resolved = self.resolve_version(version)
        if resolved not in self._models:
            self._models[resolved] = self._load_model(resolved)
            self._models[resolved].eval()
        return self._models[resolved], resolved

    def _load_model(self, version: str) -> WorldModel:
        model = WorldModel(
            self.config.active_learning.input_dim,
            self.config.active_learning.action_dim,
            encoder_config=self.config.encoder,
            predictor_config=self.config.predictor,
            memory_config=self.config.memory,
            latent_dim=self.config.encoder.latent_dim,
        )
        checkpoint_path = self._checkpoint_path(version)
        if checkpoint_path is not None and checkpoint_path.exists():
            payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
            state_dict = payload["state_dict"] if isinstance(payload, dict) and "state_dict" in payload else payload
            model.load_state_dict(state_dict)
        return model

    def _checkpoint_path(self, version: str) -> Path | None:
        models_cfg = self.config.ab_testing.models
        path_value = models_cfg.get(version)
        if not path_value:
            return None
        return Path(path_value)
