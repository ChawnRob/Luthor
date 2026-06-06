"""
Luthor Configuration Module

Centralized configuration management for Luthor WM.
Loads configuration from environment variables and provides sensible defaults.
"""

import os
from dataclasses import dataclass
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
    label_timeout_seconds: int = 3600


@dataclass
class WeatherToolConfig:
    """Weather tool configuration."""
    enabled: bool = True
    api_url: str = "https://api.open-meteo.com/v1/forecast"


@dataclass
class ToolsConfig:
    """External tool configuration."""
    weather: WeatherToolConfig


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
    tools: ToolsConfig
    debug: bool = False

    @staticmethod
    def from_params(params: dict) -> "LuthorConfig":
        visualization = params.get("visualization", {})
        logging_cfg = params.get("logging", {})

        memory_cfg = params.get("memory", {})
        tools_cfg = params.get("tools", {})
        weather_cfg = tools_cfg.get("weather", {})

        return LuthorConfig(
            encoder=EncoderConfig(**params["encoder"]),
            predictor=PredictorConfig(**params["predictor"]),
            planner=PlannerConfig(**params["planner"]),
            visualization=VisualizationConfig(**visualization),
            logging=LoggingConfig(**logging_cfg),
            active_learning=ActiveLearningConfig(**params["active_learning"]),
            memory=MemoryConfig(**memory_cfg),
            tools=ToolsConfig(weather=WeatherToolConfig(**weather_cfg)),
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
                label_timeout_seconds=int(os.getenv("LUTHOR_LABEL_TIMEOUT", "3600")),
            ),
            tools=ToolsConfig(
                weather=WeatherToolConfig(
                    enabled=os.getenv("LUTHOR_WEATHER_ENABLED", "true").lower() == "true",
                    api_url=os.getenv(
                        "LUTHOR_WEATHER_API_URL",
                        "https://api.open-meteo.com/v1/forecast",
                    ),
                ),
            ),
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
                "label_timeout_seconds": self.active_learning.label_timeout_seconds,
            },
            "tools": {
                "weather": {
                    "enabled": self.tools.weather.enabled,
                    "api_url": self.tools.weather.api_url,
                },
            },
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


def get_config() -> LuthorConfig:
    """Get the global Luthor configuration."""
    global _config
    if _config is None:
        _config = LuthorConfig.from_env()
    return _config


def reset_config():
    """Reset the global configuration (useful for testing)."""
    global _config
    _config = None
