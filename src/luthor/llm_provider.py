"""
LLM Provider Configuration Module for Luthor

Provides a provider-agnostic interface for LLM interactions.
Supports multiple providers: DeepSeek, OpenAI, OpenRouter, Kimi, Llama (local)
Default: DeepSeek API

Environment Variables:
- LUTHOR_MODEL_PROVIDER: Provider name (deepseek, openai, openrouter, kimi, llama)
- LUTHOR_DEFAULT_MODEL: Model identifier (e.g., deepseek-chat, gpt-4, etc.)
- DEEPSEEK_API_KEY: DeepSeek API key
- OPENAI_API_KEY: OpenAI API key
- OPENROUTER_API_KEY: OpenRouter API key
- KIMI_API_KEY: Kimi API key
"""

import os
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class LLMProvider(Enum):
    """Supported LLM providers."""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    KIMI = "kimi"
    LLAMA_LOCAL = "llama"  # Local fallback only


@dataclass
class LLMConfig:
    """Configuration for LLM provider."""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    # Default configurations per provider
    DEFAULT_CONFIGS = {
        LLMProvider.DEEPSEEK: {
            "api_base": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "api_key_env": "DEEPSEEK_API_KEY",
        },
        LLMProvider.OPENAI: {
            "api_base": "https://api.openai.com/v1",
            "model": "gpt-4",
            "api_key_env": "OPENAI_API_KEY",
        },
        LLMProvider.OPENROUTER: {
            "api_base": "https://openrouter.ai/api/v1",
            "model": "openrouter/auto",
            "api_key_env": "OPENROUTER_API_KEY",
        },
        LLMProvider.KIMI: {
            "api_base": "https://api.moonshot.cn/v1",
            "model": "moonshot-v1-8k",
            "api_key_env": "KIMI_API_KEY",
        },
        LLMProvider.LLAMA_LOCAL: {
            "api_base": "http://localhost:8000/v1",
            "model": "llama-2-7b",
            "api_key_env": None,  # Local, no API key needed
        },
    }

    @staticmethod
    def get_config() -> LLMConfig:
        """
        Get LLM configuration from environment variables.
        
        Returns:
            LLMConfig: Configuration for the selected provider
            
        Raises:
            ValueError: If provider is not supported or API key is missing
        """
        # Get provider from env, default to DeepSeek
        provider_name = os.getenv("LUTHOR_MODEL_PROVIDER", "deepseek").lower()
        
        try:
            provider = LLMProvider(provider_name)
        except ValueError:
            raise ValueError(
                f"Unsupported provider: {provider_name}. "
                f"Supported: {', '.join([p.value for p in LLMProvider])}"
            )

        # Get default config for provider
        default_config = LLMProviderFactory.DEFAULT_CONFIGS.get(provider)
        if not default_config:
            raise ValueError(f"No default config for provider: {provider.value}")

        # Get model from env or use default
        model = os.getenv("LUTHOR_DEFAULT_MODEL", default_config["model"])

        # Get API key if required
        api_key = None
        if default_config.get("api_key_env"):
            api_key = os.getenv(default_config["api_key_env"])
            if not api_key and provider != LLMProvider.LLAMA_LOCAL:
                raise ValueError(
                    f"API key not found. Set {default_config['api_key_env']} environment variable."
                )

        return LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            api_base=default_config.get("api_base"),
            temperature=float(os.getenv("LUTHOR_LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LUTHOR_LLM_MAX_TOKENS", "2048")),
            timeout=int(os.getenv("LUTHOR_LLM_TIMEOUT", "30")),
        )

    @staticmethod
    def create_client(config: LLMConfig) -> Any:
        """
        Create an LLM client for the specified provider.
        
        Args:
            config: LLMConfig instance
            
        Returns:
            LLM client instance (OpenAI-compatible or provider-specific)
        """
        if config.provider == LLMProvider.DEEPSEEK:
            return LLMProviderFactory._create_deepseek_client(config)
        elif config.provider == LLMProvider.OPENAI:
            return LLMProviderFactory._create_openai_client(config)
        elif config.provider == LLMProvider.OPENROUTER:
            return LLMProviderFactory._create_openrouter_client(config)
        elif config.provider == LLMProvider.KIMI:
            return LLMProviderFactory._create_kimi_client(config)
        elif config.provider == LLMProvider.LLAMA_LOCAL:
            return LLMProviderFactory._create_llama_local_client(config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")

    @staticmethod
    def _create_deepseek_client(config: LLMConfig) -> Any:
        """Create DeepSeek API client (OpenAI-compatible)."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI package required: pip install openai")

        return OpenAI(
            api_key=config.api_key,
            base_url=config.api_base,
            timeout=config.timeout,
        )

    @staticmethod
    def _create_openai_client(config: LLMConfig) -> Any:
        """Create OpenAI API client."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI package required: pip install openai")

        return OpenAI(
            api_key=config.api_key,
            timeout=config.timeout,
        )

    @staticmethod
    def _create_openrouter_client(config: LLMConfig) -> Any:
        """Create OpenRouter API client (OpenAI-compatible)."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI package required: pip install openai")

        return OpenAI(
            api_key=config.api_key,
            base_url=config.api_base,
            timeout=config.timeout,
        )

    @staticmethod
    def _create_kimi_client(config: LLMConfig) -> Any:
        """Create Kimi (Moonshot) API client (OpenAI-compatible)."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI package required: pip install openai")

        return OpenAI(
            api_key=config.api_key,
            base_url=config.api_base,
            timeout=config.timeout,
        )

    @staticmethod
    def _create_llama_local_client(config: LLMConfig) -> Any:
        """Create local Llama client (via Ollama or similar)."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI package required: pip install openai")

        return OpenAI(
            api_key="not-needed",  # Local, no auth required
            base_url=config.api_base,
            timeout=config.timeout,
        )


class LLMInterface:
    """
    Unified interface for LLM interactions.
    Abstracts away provider-specific details.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM interface.
        
        Args:
            config: LLMConfig instance. If None, loads from environment.
        """
        self.config = config or LLMProviderFactory.get_config()
        self.client = LLMProviderFactory.create_client(self.config)

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a completion for the given prompt.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Sampling temperature (optional)
            max_tokens: Maximum tokens to generate (optional)
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
        )

        return response.choices[0].message.content

    def stream_complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Generate a streaming completion for the given prompt.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Sampling temperature (optional)
            max_tokens: Maximum tokens to generate (optional)
            
        Yields:
            Generated text chunks
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider."""
        return {
            "provider": self.config.provider.value,
            "model": self.config.model,
            "api_base": self.config.api_base,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "timeout": self.config.timeout,
        }
