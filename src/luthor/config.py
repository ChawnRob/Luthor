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
class LuthorConfig:
    """Main Luthor configuration."""
    encoder: EncoderConfig
    predictor: PredictorConfig
    planner: PlannerConfig
    visualization: VisualizationConfig
    logging: LoggingConfig
    debug: bool = False

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
