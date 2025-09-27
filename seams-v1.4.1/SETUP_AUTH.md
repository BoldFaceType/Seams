# 🔐 Need an Auth Token?

You're seeing this because you need to configure authentication for Seams.

## Quick Options

### Option 1: Free Local Models (Recommended for Development)

1. **Install LM Studio**: Download from [https://lmstudio.ai/](https://lmstudio.ai/)
   - Start LM Studio and download a model
   - Go to "Developer" tab and start the server
   
2. **OR Install Ollama**: Download from [https://ollama.ai/](https://ollama.ai/)
   ```bash
   # Install a model
   ollama pull llama3.1:8b-instruct
   # Server starts automatically
   ```

3. **Auto-configure Seams**:
   ```bash
   python seams.py configure
   ```

### Option 2: Cloud API Keys (Pay-per-use)

#### OpenAI API Key
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create new key
3. Set environment variable:
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   python seams.py configure
   ```

#### Anthropic API Key  
1. Go to [https://console.anthropic.com/](https://console.anthropic.com/)
2. Create API key
3. Set environment variable:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-your-key-here"
   python seams.py configure
   ```

## Testing Your Setup

```bash
# Test the configuration
python seams.py run --name refactor_python_function --json '{
  "code": "def hello(): print(\"world\")",
  "goal": "add docstring",
  "constraints": [],
  "seed": 1
}'
```

## Need More Help?

See the comprehensive guide: [**../AUTH_TOKENS.md**](../AUTH_TOKENS.md)

---

*This file: `SETUP_AUTH.md` - Quick authentication setup guide*