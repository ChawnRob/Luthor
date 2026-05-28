"""
DeepSeek Integration Module for Luthor

Provides DeepSeek-specific functionality while maintaining provider-agnostic interface.
DeepSeek is the default provider for Luthor WM.

API Documentation: https://platform.deepseek.com/api-docs
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from luthor.llm_provider import LLMInterface, LLMConfig, LLMProvider


@dataclass
class DeepSeekConfig:
    """DeepSeek-specific configuration."""
    api_key: str
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


class DeepSeekIntegration:
    """
    DeepSeek integration for Luthor WM.
    
    Features:
    - Reasoning models support
    - Context window: up to 64K tokens
    - Cost-effective for PME/SMB
    - Fast inference
    """

    # Available DeepSeek models
    MODELS = {
        "deepseek-chat": {
            "description": "Fast general-purpose model",
            "context_window": 64000,
            "supports_reasoning": False,
        },
        "deepseek-reasoner": {
            "description": "Reasoning model for complex tasks",
            "context_window": 64000,
            "supports_reasoning": True,
        },
    }

    def __init__(self, config: Optional[DeepSeekConfig] = None):
        """
        Initialize DeepSeek integration.
        
        Args:
            config: DeepSeekConfig instance. If None, loads from environment.
        """
        if config is None:
            config = self._load_config_from_env()
        
        self.config = config
        
        # Create LLM interface with DeepSeek provider
        llm_config = LLMConfig(
            provider=LLMProvider.DEEPSEEK,
            model=config.model,
            api_key=config.api_key,
            api_base="https://api.deepseek.com/v1",
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
        
        self.llm = LLMInterface(llm_config)

    @staticmethod
    def _load_config_from_env() -> DeepSeekConfig:
        """Load configuration from environment variables."""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY environment variable not set. "
                "Get your key from https://platform.deepseek.com"
            )

        return DeepSeekConfig(
            api_key=api_key,
            model=os.getenv("LUTHOR_DEFAULT_MODEL", "deepseek-chat"),
            temperature=float(os.getenv("LUTHOR_LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LUTHOR_LLM_MAX_TOKENS", "2048")),
            top_p=float(os.getenv("DEEPSEEK_TOP_P", "1.0")),
            frequency_penalty=float(os.getenv("DEEPSEEK_FREQUENCY_PENALTY", "0.0")),
            presence_penalty=float(os.getenv("DEEPSEEK_PRESENCE_PENALTY", "0.0")),
        )

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_reasoning: bool = False,
    ) -> str:
        """
        Generate a completion using DeepSeek.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            use_reasoning: Use reasoning model if available (optional)
            
        Returns:
            Generated text
        """
        if use_reasoning and "reasoner" not in self.config.model:
            # Switch to reasoning model if requested
            original_model = self.llm.config.model
            self.llm.config.model = "deepseek-reasoner"
            result = self.llm.complete(prompt, system_prompt)
            self.llm.config.model = original_model
            return result
        
        return self.llm.complete(prompt, system_prompt)

    def stream_complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_reasoning: bool = False,
    ):
        """
        Generate a streaming completion using DeepSeek.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            use_reasoning: Use reasoning model if available (optional)
            
        Yields:
            Generated text chunks
        """
        if use_reasoning and "reasoner" not in self.config.model:
            # Switch to reasoning model if requested
            original_model = self.llm.config.model
            self.llm.config.model = "deepseek-reasoner"
            yield from self.llm.stream_complete(prompt, system_prompt)
            self.llm.config.model = original_model
        else:
            yield from self.llm.stream_complete(prompt, system_prompt)

    def analyze_world_state(self, state_description: str) -> str:
        """
        Analyze a world state description using DeepSeek reasoning.
        
        Args:
            state_description: Description of the current world state
            
        Returns:
            Analysis and recommendations
        """
        system_prompt = """You are an expert AI analyzing world states for an agentic world model.
Provide:
1. Current state analysis
2. Key factors and dependencies
3. Potential next states
4. Confidence levels"""

        return self.complete(
            state_description,
            system_prompt=system_prompt,
            use_reasoning=True,
        )

    def plan_actions(
        self,
        goal: str,
        current_state: str,
        available_actions: List[str],
    ) -> str:
        """
        Plan actions to reach a goal using DeepSeek.
        
        Args:
            goal: Target goal
            current_state: Current world state
            available_actions: List of available actions
            
        Returns:
            Action plan
        """
        system_prompt = """You are an expert planner for an agentic world model.
Given a goal, current state, and available actions, provide:
1. Step-by-step action plan
2. Expected outcomes
3. Risk assessment
4. Alternative strategies"""

        prompt = f"""Goal: {goal}

Current State: {current_state}

Available Actions:
{chr(10).join(f'- {action}' for action in available_actions)}

Provide a detailed action plan."""

        return self.complete(
            prompt,
            system_prompt=system_prompt,
            use_reasoning=True,
        )

    def evaluate_trajectory(
        self,
        trajectory: List[Dict[str, Any]],
        goal: str,
    ) -> str:
        """
        Evaluate a trajectory of states and actions.
        
        Args:
            trajectory: List of {state, action, next_state} dicts
            goal: Target goal
            
        Returns:
            Evaluation and recommendations
        """
        system_prompt = """You are an expert evaluator of action trajectories.
Analyze the trajectory and provide:
1. Efficiency assessment
2. Goal achievement likelihood
3. Improvement suggestions
4. Alternative paths"""

        trajectory_str = "\n".join(
            f"Step {i}: {step['action']} -> {step['next_state']}"
            for i, step in enumerate(trajectory, 1)
        )

        prompt = f"""Evaluate this trajectory toward goal: {goal}

{trajectory_str}

Provide detailed evaluation and recommendations."""

        return self.complete(
            prompt,
            system_prompt=system_prompt,
            use_reasoning=True,
        )

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current DeepSeek model."""
        model_info = self.MODELS.get(self.config.model, {})
        return {
            "provider": "deepseek",
            "model": self.config.model,
            "description": model_info.get("description", "Unknown"),
            "context_window": model_info.get("context_window", 64000),
            "supports_reasoning": model_info.get("supports_reasoning", False),
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

    @staticmethod
    def get_available_models() -> Dict[str, Dict[str, Any]]:
        """Get information about all available DeepSeek models."""
        return DeepSeekIntegration.MODELS


# Convenience function for quick DeepSeek access
def get_deepseek() -> DeepSeekIntegration:
    """Get a DeepSeek integration instance."""
    return DeepSeekIntegration()
