"""
Luthor Configuration Module

Centralized configuration management for Luthor WM.
Loads configuration from environment variables and provides sensible defaults.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class EncoderConfig:
    """Encoder configuration."""
    latent_dim: int = 128
    hidden_dim: int = 256
    num_layers: int = 2
    dropout: float = 0.1


@dataclass
class PredictorConfig:
    """Predictor configuration."""
    hidden_dim: int = 256
    num_layers: int = 3
    dropout: float = 0.1
    use_attention: bool = True
    predictor_type: str = "mlp"
    linear_attention_dim_head: int = 32
    linear_attention_heads: int = 4
    feature_map: str = "elu+1"


@dataclass
class PlannerConfig:
    """Planner configuration."""
    horizon: int = 10
    num_samples: int = 100
    learning_rate: float = 0.001
    num_iterations: int = 100


@dataclass
class VisualizationConfig:
    """Visualization configuration."""
    enabled: bool = True
    output_dir: str = "./outputs"
    save_plots: bool = True
    show_plots: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    log_file: Optional[str] = None
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class ActiveLearningConfig:
    """Active learning loop configuration (JEPA SLM skeleton)."""
    num_rounds: int = 10
    pool_size: int = 32
    query_batch_size: int = 8
    mc_samples: int = 10
    train_steps_per_round: int = 5
    input_dim: int = 2
    action_dim: int = 2
    human_in_loop: bool = False


@dataclass
class ABTestingConfig:
    """A/B testing configuration for model variants."""
    enabled: bool = False
    models: dict[str, str] = field(
        default_factory=lambda: {
            "default": "models/jepa_model.pth",
            "candidate": "models/jepa_model_v2.pth",
        }
    )


@dataclass
class MemoryConfig:
    """Context compression (GRU memory) configuration."""
    use_context_compression: bool = False
    history_length: int = 8
    gru_hidden_dim: int = 64
    gru_num_layers: int = 1
    compress_source: str = "observation"


@dataclass
class LuthorConfig:
    """Main Luthor configuration."""
    encoder: EncoderConfig
    predictor: PredictorConfig
    planner: PlannerConfig
    visualization: VisualizationConfig
    logging: LoggingConfig
    active_learning: ActiveLearningConfig
    memory: MemoryConfig
    ab_testing: ABTestingConfig
    prompt_version: str = "v1"
    debug: bool = False

    @staticmethod
    def from_params(params: dict) -> "LuthorConfig":
        visualization = params.get("visualization", {})
        logging_cfg = params.get("logging", {})

        memory_cfg = params.get("memory", {})
        ab_cfg = params.get("ab_testing", {})
        ab_models = ab_cfg.get("models", {})

        return LuthorConfig(
            encoder=EncoderConfig(**params["encoder"]),
            predictor=PredictorConfig(**params["predictor"]),
            planner=PlannerConfig(**params["planner"]),
            visualization=VisualizationConfig(**visualization),
            logging=LoggingConfig(**logging_cfg),
            active_learning=ActiveLearningConfig(**params["active_learning"]),
            memory=MemoryConfig(**memory_cfg),
            ab_testing=ABTestingConfig(
                enabled=bool(ab_cfg.get("enabled", False)),
                models={
                    "default": ab_models.get("default", "models/jepa_model.pth"),
                    "candidate": ab_models.get("candidate", "models/jepa_model_v2.pth"),
                },
            ),
            prompt_version=str(params.get("prompt_version", "v1")),
            debug=params.get("debug", False),
        )

    @staticmethod
    def from_env() -> "LuthorConfig":
        """Load configuration from environment variables."""
        return LuthorConfig(
            encoder=EncoderConfig(
                latent_dim=int(os.getenv("LUTHOR_ENCODER_LATENT_DIM", "128")),
                hidden_dim=int(os.getenv("LUTHOR_ENCODER_HIDDEN_DIM", "256")),
                num_layers=int(os.getenv("LUTHOR_ENCODER_NUM_LAYERS", "2")),
                dropout=float(os.getenv("LUTHOR_ENCODER_DROPOUT", "0.1")),
            ),
            predictor=PredictorConfig(
                hidden_dim=int(os.getenv("LUTHOR_PREDICTOR_HIDDEN_DIM", "256")),
                num_layers=int(os.getenv("LUTHOR_PREDICTOR_LAYERS", "3")),
                dropout=float(os.getenv("LUTHOR_PREDICTOR_DROPOUT", "0.1")),
                use_attention=os.getenv("LUTHOR_PREDICTOR_USE_ATTENTION", "true").lower() == "true",
                predictor_type=os.getenv("LUTHOR_PREDICTOR_TYPE", "mlp"),
                linear_attention_dim_head=int(os.getenv("LUTHOR_LINEAR_ATTENTION_DIM_HEAD", "32")),
                linear_attention_heads=int(os.getenv("LUTHOR_LINEAR_ATTENTION_HEADS", "4")),
                feature_map=os.getenv("LUTHOR_LINEAR_ATTENTION_FEATURE_MAP", "elu+1"),
            ),
            planner=PlannerConfig(
                horizon=int(os.getenv("LUTHOR_PLANNER_HORIZON", "10")),
                num_samples=int(os.getenv("LUTHOR_PLANNER_NUM_SAMPLES", "100")),
                learning_rate=float(os.getenv("LUTHOR_PLANNER_LR", "0.001")),
                num_iterations=int(os.getenv("LUTHOR_PLANNER_ITERATIONS", "100")),
            ),
            visualization=VisualizationConfig(
                enabled=os.getenv("LUTHOR_VISUALIZATION_ENABLED", "true").lower() == "true",
                output_dir=os.getenv("LUTHOR_VISUALIZATION_OUTPUT_DIR", "./outputs"),
                save_plots=os.getenv("LUTHOR_VISUALIZATION_SAVE_PLOTS", "true").lower() == "true",
                show_plots=os.getenv("LUTHOR_VISUALIZATION_SHOW_PLOTS", "false").lower() == "true",
            ),
            logging=LoggingConfig(
                level=os.getenv("LUTHOR_LOG_LEVEL", "INFO"),
                log_file=os.getenv("LUTHOR_LOG_FILE"),
                format=os.getenv(
                    "LUTHOR_LOG_FORMAT",
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                ),
            ),
            active_learning=ActiveLearningConfig(
                num_rounds=int(os.getenv("LUTHOR_AL_ROUNDS", "10")),
                pool_size=int(os.getenv("LUTHOR_AL_POOL_SIZE", "32")),
                query_batch_size=int(os.getenv("LUTHOR_AL_QUERY_BATCH", "8")),
                mc_samples=int(os.getenv("LUTHOR_AL_MC_SAMPLES", "10")),
                train_steps_per_round=int(os.getenv("LUTHOR_AL_TRAIN_STEPS", "5")),
                input_dim=int(os.getenv("LUTHOR_AL_INPUT_DIM", "2")),
                action_dim=int(os.getenv("LUTHOR_AL_ACTION_DIM", "2")),
                human_in_loop=os.getenv("LUTHOR_HUMAN_IN_LOOP", "false").lower() == "true",
            ),
            ab_testing=ABTestingConfig(
                enabled=os.getenv("LUTHOR_AB_TESTING_ENABLED", "false").lower() == "true",
                models={
                    "default": os.getenv("LUTHOR_AB_MODEL_DEFAULT", "models/jepa_model.pth"),
                    "candidate": os.getenv("LUTHOR_AB_MODEL_CANDIDATE", "models/jepa_model_v2.pth"),
                },
            ),
            prompt_version=os.getenv("LUTHOR_PROMPT_VERSION", "v1"),
            memory=MemoryConfig(
                use_context_compression=os.getenv(
                    "LUTHOR_USE_CONTEXT_COMPRESSION", "false"
                ).lower()
                == "true",
                history_length=int(os.getenv("LUTHOR_HISTORY_LENGTH", "8")),
                gru_hidden_dim=int(os.getenv("LUTHOR_GRU_HIDDEN_DIM", "64")),
                gru_num_layers=int(os.getenv("LUTHOR_GRU_NUM_LAYERS", "1")),
                compress_source=os.getenv("LUTHOR_COMPRESS_SOURCE", "observation"),
            ),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "encoder": {
                "latent_dim": self.encoder.latent_dim,
                "hidden_dim": self.encoder.hidden_dim,
                "num_layers": self.encoder.num_layers,
                "dropout": self.encoder.dropout,
            },
            "predictor": {
                "hidden_dim": self.predictor.hidden_dim,
                "num_layers": self.predictor.num_layers,
                "dropout": self.predictor.dropout,
                "use_attention": self.predictor.use_attention,
                "predictor_type": self.predictor.predictor_type,
                "linear_attention_dim_head": self.predictor.linear_attention_dim_head,
                "linear_attention_heads": self.predictor.linear_attention_heads,
                "feature_map": self.predictor.feature_map,
            },
            "planner": {
                "horizon": self.planner.horizon,
                "num_samples": self.planner.num_samples,
                "learning_rate": self.planner.learning_rate,
                "num_iterations": self.planner.num_iterations,
            },
            "visualization": {
                "enabled": self.visualization.enabled,
                "output_dir": self.visualization.output_dir,
                "save_plots": self.visualization.save_plots,
                "show_plots": self.visualization.show_plots,
            },
            "logging": {
                "level": self.logging.level,
                "log_file": self.logging.log_file,
                "format": self.logging.format,
            },
            "active_learning": {
                "num_rounds": self.active_learning.num_rounds,
                "pool_size": self.active_learning.pool_size,
                "query_batch_size": self.active_learning.query_batch_size,
                "mc_samples": self.active_learning.mc_samples,
                "train_steps_per_round": self.active_learning.train_steps_per_round,
                "input_dim": self.active_learning.input_dim,
                "action_dim": self.active_learning.action_dim,
                "human_in_loop": self.active_learning.human_in_loop,
            },
            "ab_testing": {
                "enabled": self.ab_testing.enabled,
                "models": self.ab_testing.models,
            },
            "prompt_version": self.prompt_version,
            "memory": {
                "use_context_compression": self.memory.use_context_compression,
                "history_length": self.memory.history_length,
                "gru_hidden_dim": self.memory.gru_hidden_dim,
                "gru_num_layers": self.memory.gru_num_layers,
                "compress_source": self.memory.compress_source,
            },
            "debug": self.debug,
        }


# Global configuration instance
_config: Optional[LuthorConfig] = None


def _default_params_path() -> Path | None:
    override = os.getenv("LUTHOR_PARAMS_PATH")
    if override:
        path = Path(override)
        return path if path.exists() else None

    repo_root = Path(__file__).resolve().parents[2]
    candidate = repo_root / "params.yaml"
    return candidate if candidate.exists() else None


def _merge_predictor_config(config: LuthorConfig, predictor_params: dict) -> None:
    if not predictor_params:
        return
    merged = {**config.predictor.__dict__, **predictor_params}
    allowed = PredictorConfig.__dataclass_fields__.keys()
    config.predictor = PredictorConfig(**{key: merged[key] for key in allowed})


def _merge_params_into_config(config: LuthorConfig, params: dict) -> LuthorConfig:
    config.prompt_version = str(params.get("prompt_version", config.prompt_version))
    _merge_predictor_config(config, params.get("predictor", {}))

    ab_cfg = params.get("ab_testing", {})
    if ab_cfg:
        config.ab_testing.enabled = bool(ab_cfg.get("enabled", config.ab_testing.enabled))
        models = ab_cfg.get("models", {})
        if models:
            config.ab_testing.models = {
                "default": models.get("default", config.ab_testing.models["default"]),
                "candidate": models.get("candidate", config.ab_testing.models["candidate"]),
            }

    al_cfg = params.get("active_learning", {})
    if "human_in_loop" in al_cfg:
        config.active_learning.human_in_loop = bool(al_cfg["human_in_loop"])

    return config


def get_config() -> LuthorConfig:
    """Get the global Luthor configuration."""
    global _config
    if _config is None:
        _config = LuthorConfig.from_env()
        params_path = _default_params_path()
        if params_path is not None:
            from luthor.pipeline.params import load_params

            _config = _merge_params_into_config(_config, load_params(params_path))

        if os.getenv("LUTHOR_AB_TESTING_ENABLED") is not None:
            _config.ab_testing.enabled = (
                os.getenv("LUTHOR_AB_TESTING_ENABLED", "false").lower() == "true"
            )
        if os.getenv("LUTHOR_PROMPT_VERSION") is not None:
            _config.prompt_version = os.getenv("LUTHOR_PROMPT_VERSION", "v1")
        if os.getenv("LUTHOR_PREDICTOR_TYPE") is not None:
            _config.predictor.predictor_type = os.getenv("LUTHOR_PREDICTOR_TYPE", "mlp")
    return _config


def reset_config():
    """Reset the global configuration (useful for testing)."""
    global _config
    _config = None
