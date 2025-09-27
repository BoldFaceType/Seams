# Authentication Guide - How to Get and Configure Auth Tokens

This guide explains how to get and configure authentication tokens for the Seams system.

## Overview

Seams supports multiple AI providers and authentication methods:
1. **OpenAI API** (gpt-4o-mini, etc.) - requires API key
2. **Anthropic API** (Claude models) - requires API key  
3. **Local Models** (LM Studio, Ollama) - no authentication needed
4. **Stub Mode** - no authentication, for testing

## Quick Setup

The easiest way to configure authentication is to run:

```bash
cd seams-v1.4.1
python seams.py configure
```

This will auto-detect local models (LM Studio/Ollama) or fall back to cloud providers if you have API keys configured.

## Getting API Keys

### 1. OpenAI API Key

**Where to get it:**
- Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Sign in to your OpenAI account (create one if needed)
- Click "Create new secret key"
- Give it a name (e.g., "Seams Development")
- Copy the key (starts with `sk-`)

**How much it costs:**
- Pay-per-use pricing
- GPT-4o-mini: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- See current pricing at [https://openai.com/api/pricing/](https://openai.com/api/pricing/)

**How to configure:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### 2. Anthropic API Key

**Where to get it:**
- Go to [https://console.anthropic.com/](https://console.anthropic.com/)
- Sign in to your Anthropic account (create one if needed)
- Go to "API Keys" section
- Click "Create Key"
- Copy the key (starts with `sk-ant-`)

**How much it costs:**
- Pay-per-use pricing
- Claude 3 Haiku: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens
- See current pricing at [https://www.anthropic.com/api](https://www.anthropic.com/api)

**How to configure:**
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### 3. Local Models (Free Alternative)

**LM Studio:**
- Download from [https://lmstudio.ai/](https://lmstudio.ai/)
- Install and start the local server on default port 1234
- No API key required

**Ollama:**
- Install from [https://ollama.ai/](https://ollama.ai/)
- Start the server (default port 11434)
- No API key required

## Configuration Methods

### Method 1: Environment Variables (Recommended)

Set environment variables before running Seams:

```bash
# For OpenAI
export OPENAI_API_KEY="sk-your-openai-key"

# For Anthropic  
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"

# Optional: Override other settings
export SEAMS_BACKEND="openai"           # Force specific backend
export SEAMS_MODEL="gpt-4o-mini"        # Force specific model
export SEAMS_OPENAI_BASE_URL="..."      # Custom OpenAI-compatible endpoint
export SEAMS_HTTP_TIMEOUT="60"          # HTTP timeout in seconds
```

### Method 2: Auto-Detection

Run the configure command to auto-detect your setup:

```bash
cd seams-v1.4.1
python seams.py configure
```

This creates a `seams.local.json` file with detected configuration.

### Method 3: Manual Configuration File

Create `seams-v1.4.1/seams.local.json`:

```json
{
  "backend": "openai",
  "model": "gpt-4o-mini"
}
```

Or for Anthropic:

```json
{
  "backend": "anthropic", 
  "model": "claude-3-haiku-20240307"
}
```

Or for local models:

```json
{
  "backend": "openai_compat",
  "openai_base_url": "http://127.0.0.1:1234/v1",
  "model": "llama-3.1-8b-instruct"
}
```

## Testing Your Configuration

### Test the CLI:
```bash
cd seams-v1.4.1
python seams.py run --name refactor_python_function --json '{
  "code": "def f(x): return x+1", 
  "goal": "clarify", 
  "constraints": ["pep8"], 
  "seed": 1
}'
```

### Test the Server:
```bash
cd seams-v1.4.1/agent-core
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn agent_server:app --host 127.0.0.1 --port 8765

# In another terminal:
curl http://127.0.0.1:8765/healthz
```

## Priority Order

Seams uses this priority order for configuration:

1. **Environment variables** (highest priority)
   - `SEAMS_BACKEND`, `SEAMS_MODEL`, etc.
2. **Local file** (`seams.local.json`)
3. **Auto-detection**
   - Local servers (LM Studio on :1234, Ollama on :11434)  
   - Cloud providers (if `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` set)
4. **Stub mode** (lowest priority - for testing)

## Troubleshooting

### "ModuleNotFoundError: No module named 'httpx'"

Install dependencies first:
```bash
cd seams-v1.4.1/agent-core
pip install -e .
```

### API Key Not Working

1. Check the key format:
   - OpenAI keys start with `sk-`
   - Anthropic keys start with `sk-ant-`

2. Check the key is set correctly:
   ```bash
   echo $OPENAI_API_KEY
   echo $ANTHROPIC_API_KEY
   ```

3. Check your account has credits/billing set up

### Local Models Not Detected  

1. Make sure LM Studio or Ollama is running
2. Test the endpoint manually:
   ```bash
   curl http://127.0.0.1:1234/v1/models  # LM Studio
   curl http://127.0.0.1:11434/v1/models # Ollama
   ```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** or secure secret management
3. **Rotate keys periodically**
4. **Monitor usage** on provider dashboards to detect unexpected usage
5. **Use local models** for sensitive code when possible

## Cost Management

- **Start with local models** (free) for development
- **Use cheaper models** (like gpt-4o-mini, claude-haiku) for experimentation  
- **Monitor usage** on OpenAI/Anthropic dashboards
- **Set billing limits** on provider accounts
- **Consider caching** for repeated operations