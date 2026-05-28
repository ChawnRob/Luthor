# Luthor LLM Provider Strategy

## Overview

Luthor WM now features a **provider-agnostic LLM infrastructure** with **DeepSeek as the default provider**. This design allows seamless switching between multiple LLM providers while maintaining a unified interface.

## Why DeepSeek as Default?

**Cost Efficiency for SMBs/PMEs:**
- DeepSeek offers competitive pricing compared to OpenAI/Claude
- Suitable for cost-conscious organizations
- Fast inference with reasonable latency

**Technical Advantages:**
- 64K token context window
- Reasoning model support
- OpenAI-compatible API (easy integration)
- Reliable uptime and performance

**Comparison:**

| Provider | Cost | Speed | Quality | Context | Reasoning |
|----------|------|-------|---------|---------|-----------|
| **DeepSeek** | ✅ Low | ✅ Fast | ✅ Good | 64K | ✅ Yes |
| OpenAI (GPT-4) | ❌ High | ⚠️ Moderate | ✅ Excellent | 128K | ✅ Yes |
| Claude (Anthropic) | ❌ Very High | ⚠️ Slow | ✅ Excellent | 200K | ⚠️ Limited |
| OpenRouter | ✅ Moderate | ✅ Fast | ✅ Good | Varies | Varies |
| Kimi | ✅ Low | ✅ Fast | ✅ Good | 200K | ⚠️ Limited |

## Architecture

### Provider-Agnostic Design

```
┌─────────────────────────────────────────┐
│         Luthor Application              │
├─────────────────────────────────────────┤
│         LLMInterface (Unified)          │
├─────────────────────────────────────────┤
│      LLMProviderFactory (Router)        │
├──────────────┬──────────────┬───────────┤
│  DeepSeek    │   OpenAI     │  OpenRouter│
│  (Default)   │  (Optional)  │ (Optional) │
└──────────────┴──────────────┴───────────┘
```

### Key Components

1. **LLMProvider (Enum)**: Defines supported providers
2. **LLMConfig (Dataclass)**: Configuration for any provider
3. **LLMProviderFactory**: Creates provider-specific clients
4. **LLMInterface**: Unified interface for all providers
5. **DeepSeekIntegration**: DeepSeek-specific features

## Configuration

### Environment Variables

**Required:**
```bash
DEEPSEEK_API_KEY=your_api_key_here
```

**Optional:**
```bash
LUTHOR_MODEL_PROVIDER=deepseek          # Default provider
LUTHOR_DEFAULT_MODEL=deepseek-chat      # Default model
LUTHOR_LLM_TEMPERATURE=0.7              # Sampling temperature
LUTHOR_LLM_MAX_TOKENS=2048              # Max output tokens
LUTHOR_LLM_TIMEOUT=30                   # Request timeout (seconds)
```

### Setup Instructions

1. **Get DeepSeek API Key:**
   - Visit https://platform.deepseek.com
   - Create an account
   - Generate API key
   - Set environment variable: `export DEEPSEEK_API_KEY=your_key`

2. **Copy .env.example:**
   ```bash
   cp .env.example .env
   # Edit .env and fill in your DEEPSEEK_API_KEY
   ```

3. **Verify Configuration:**
   ```bash
   python3 -c "from luthor import get_deepseek; ds = get_deepseek(); print(ds.get_model_info())"
   ```

## Usage Examples

### Using DeepSeek (Default)

```python
from luthor import get_deepseek

# Initialize DeepSeek
deepseek = get_deepseek()

# Simple completion
response = deepseek.complete(
    prompt="Analyze this world state: ...",
    system_prompt="You are an expert world model analyzer."
)
print(response)

# With reasoning (uses deepseek-reasoner model)
response = deepseek.complete(
    prompt="Complex reasoning task...",
    use_reasoning=True
)

# Streaming
for chunk in deepseek.stream_complete("Your prompt here"):
    print(chunk, end="", flush=True)
```

### Using Provider-Agnostic Interface

```python
from luthor import LLMInterface

# Automatically uses LUTHOR_MODEL_PROVIDER (default: deepseek)
llm = LLMInterface()

# Works with any provider
response = llm.complete("Your prompt here")

# Get provider info
info = llm.get_provider_info()
print(f"Using {info['provider']} model: {info['model']}")
```

### Switching Providers

```python
import os
from luthor import LLMInterface, LLMProviderFactory

# Switch to OpenAI
os.environ["LUTHOR_MODEL_PROVIDER"] = "openai"
os.environ["OPENAI_API_KEY"] = "your_openai_key"

# Create new interface (will use OpenAI)
llm = LLMInterface()
response = llm.complete("Your prompt here")
```

### World Model Analysis with DeepSeek

```python
from luthor import get_deepseek

deepseek = get_deepseek()

# Analyze world state
state = """
Current state: Robot at position (10, 20)
Goal: Reach position (50, 50)
Obstacles: Wall at (30, 25)
Available actions: move_forward, turn_left, turn_right
"""

analysis = deepseek.analyze_world_state(state)
print(analysis)

# Plan actions
goal = "Reach position (50, 50) avoiding obstacles"
current_state = "Robot at (10, 20), facing north"
actions = ["move_forward", "turn_left", "turn_right"]

plan = deepseek.plan_actions(goal, current_state, actions)
print(plan)
```

## Supported Providers

### 1. DeepSeek (Default)

**Status:** ✅ Production Ready
**Models:**
- `deepseek-chat`: Fast general-purpose model
- `deepseek-reasoner`: Reasoning model for complex tasks

**Setup:**
```bash
export DEEPSEEK_API_KEY=your_key
export LUTHOR_MODEL_PROVIDER=deepseek
export LUTHOR_DEFAULT_MODEL=deepseek-chat
```

### 2. OpenAI

**Status:** ✅ Supported
**Models:** gpt-4, gpt-3.5-turbo, etc.

**Setup:**
```bash
export OPENAI_API_KEY=your_key
export LUTHOR_MODEL_PROVIDER=openai
export LUTHOR_DEFAULT_MODEL=gpt-4
```

### 3. OpenRouter

**Status:** ✅ Supported
**Models:** 100+ models from various providers

**Setup:**
```bash
export OPENROUTER_API_KEY=your_key
export LUTHOR_MODEL_PROVIDER=openrouter
export LUTHOR_DEFAULT_MODEL=openrouter/auto
```

### 4. Kimi (Moonshot)

**Status:** ✅ Supported
**Models:** moonshot-v1-8k, moonshot-v1-32k, etc.

**Setup:**
```bash
export KIMI_API_KEY=your_key
export LUTHOR_MODEL_PROVIDER=kimi
export LUTHOR_DEFAULT_MODEL=moonshot-v1-8k
```

### 5. Llama (Local)

**Status:** ✅ Supported (Fallback Only)
**Requirements:** Ollama or similar local LLM server

**Setup:**
```bash
# Start Ollama
ollama serve

# In another terminal
export LUTHOR_MODEL_PROVIDER=llama
export LUTHOR_DEFAULT_MODEL=llama-2-7b
```

## Adding New Providers

To add a new provider (e.g., Claude, Gemini):

1. **Update LLMProvider Enum** in `llm_provider.py`:
   ```python
   class LLMProvider(Enum):
       CLAUDE = "claude"
   ```

2. **Add Default Config** in `LLMProviderFactory`:
   ```python
   LLMProvider.CLAUDE: {
       "api_base": "https://api.anthropic.com/v1",
       "model": "claude-3-opus",
       "api_key_env": "ANTHROPIC_API_KEY",
   }
   ```

3. **Implement Client Factory** method:
   ```python
   @staticmethod
   def _create_claude_client(config: LLMConfig) -> Any:
       from anthropic import Anthropic
       return Anthropic(api_key=config.api_key)
   ```

4. **Update Documentation** and `.env.example`

## Performance Considerations

### Latency

- **DeepSeek:** 1-3 seconds (typical)
- **OpenAI:** 2-5 seconds (typical)
- **Local Llama:** <1 second (depends on hardware)

### Cost Estimation (per 1M tokens)

- **DeepSeek:** $0.14 (input) / $0.28 (output)
- **OpenAI GPT-4:** $30 (input) / $60 (output)
- **Claude 3 Opus:** $15 (input) / $75 (output)
- **Local Llama:** $0 (one-time hardware cost)

### Recommended Use Cases

| Provider | Best For |
|----------|----------|
| **DeepSeek** | SMBs, cost-sensitive, general tasks |
| **OpenAI** | High quality, complex reasoning |
| **OpenRouter** | Provider flexibility, cost optimization |
| **Kimi** | Chinese users, long context |
| **Llama** | Privacy-critical, air-gapped systems |

## Troubleshooting

### "API key not found" Error

```bash
# Check if environment variable is set
echo $DEEPSEEK_API_KEY

# If empty, set it
export DEEPSEEK_API_KEY=your_actual_key
```

### "Unsupported provider" Error

```bash
# Check valid providers
python3 -c "from luthor.llm_provider import LLMProvider; print([p.value for p in LLMProvider])"

# Use one of the supported providers
export LUTHOR_MODEL_PROVIDER=deepseek
```

### Connection Timeout

```bash
# Increase timeout
export LUTHOR_LLM_TIMEOUT=60

# Check API status
curl https://api.deepseek.com/v1/models
```

### Rate Limiting

```bash
# Add retry logic and exponential backoff
# (Implemented in LLMInterface by default)

# Or reduce request frequency
export LUTHOR_LLM_MAX_TOKENS=1024  # Smaller responses
```

## Migration from Llama 3 to DeepSeek

If you were previously using Llama 3:

1. **Remove Local Llama Setup:**
   ```bash
   # Stop Ollama if running
   killall ollama
   ```

2. **Get DeepSeek API Key:**
   - Visit https://platform.deepseek.com
   - Create account and generate key

3. **Update Environment:**
   ```bash
   export LUTHOR_MODEL_PROVIDER=deepseek
   export DEEPSEEK_API_KEY=your_key
   ```

4. **Verify Setup:**
   ```bash
   python3 -c "from luthor import get_deepseek; print(get_deepseek().get_model_info())"
   ```

**Benefits of Migration:**
- ✅ No local resource overhead
- ✅ Faster inference
- ✅ Lower operational cost
- ✅ Better reasoning capabilities
- ✅ Easier deployment to cloud

## References

- [DeepSeek API Documentation](https://platform.deepseek.com/api-docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Kimi API Documentation](https://platform.moonshot.cn/docs)
- [Ollama Documentation](https://ollama.ai)

---

**Last Updated:** May 2026
**Version:** 1.0.0
**Author:** Manus AI
