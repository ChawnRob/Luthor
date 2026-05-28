"""
Luthor - Agentic World Model

A production-ready implementation of Joint Embedding Predictive Architecture (JEPA)
with support for multiple LLM providers (DeepSeek, OpenAI, OpenRouter, Kimi, Llama).

Default Configuration:
- LLM Provider: DeepSeek (cost-effective for SMBs)
- Model: deepseek-chat
- Architecture: JEPA with latent prediction
- Planner: Model Predictive Control (MPC)

Quick Start:
    from luthor import get_deepseek, LuthorConfig
    
    # Get DeepSeek integration
    deepseek = get_deepseek()
    response = deepseek.complete("Analyze this world state...")
    
    # Or use provider-agnostic interface
    from luthor import LLMInterface
    llm = LLMInterface()
    response = llm.complete("Your prompt here")
"""

__version__ = "1.0.0"
__author__ = "Manus AI"

# Core JEPA components
from luthor.jepa_model.encoder import Encoder
from luthor.jepa_model.predictor import LatentPredictor
from luthor.jepa_model.planner import MPCPlanner
from luthor.jepa_model.world_model import WorldModel

# LLM Provider infrastructure
from luthor.llm_provider import (
    LLMProvider,
    LLMConfig,
    LLMProviderFactory,
    LLMInterface,
)

# DeepSeek integration (default)
from luthor.deepseek_integration import (
    DeepSeekIntegration,
    DeepSeekConfig,
    get_deepseek,
)

# Configuration
from luthor.config import (
    LuthorConfig,
    EncoderConfig,
    PredictorConfig,
    PlannerConfig,
    VisualizationConfig,
    LoggingConfig,
    get_config,
    reset_config,
)

# Environment
from luthor.environment.simple_env import SimpleEnvironment

# Utilities
from luthor.utils.cost_function import CostFunction
from luthor.utils.visualizer import Visualizer

__all__ = [
    # JEPA Components
    "Encoder",
    "LatentPredictor",
    "MPCPlanner",
    "WorldModel",
    # LLM Providers
    "LLMProvider",
    "LLMConfig",
    "LLMProviderFactory",
    "LLMInterface",
    # DeepSeek (Default)
    "DeepSeekIntegration",
    "DeepSeekConfig",
    "get_deepseek",
    # Configuration
    "LuthorConfig",
    "EncoderConfig",
    "PredictorConfig",
    "PlannerConfig",
    "VisualizationConfig",
    "LoggingConfig",
    "get_config",
    "reset_config",
    # Environment
    "SimpleEnvironment",
    # Utilities
    "CostFunction",
    "Visualizer",
]
