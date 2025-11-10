# Environment Configuration Guide

This project uses environment-specific configuration files for different deployment scenarios.

## Environment Files

- **`.env`** - Active environment configuration (git-ignored, contains your actual API keys)
- **`.env.example`** - Template file with all available options (safe to commit)
- **`.env.production`** - Production environment settings
- **`.env.test`** - Test environment settings

## Quick Start

### 1. Initial Setup

```bash
# Copy the example file to create your .env
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

### 2. Switch Between Environments

Use the helper script to switch between environments:

```bash
# Switch to development (default)
./scripts/use-env.sh dev

# Switch to production
./scripts/use-env.sh prod

# Switch to test
./scripts/use-env.sh test
```

Or manually copy the files:

```bash
# Development
cp .env.example .env

# Production
cp .env.production .env

# Test
cp .env.test .env
```

## Environment Configurations

### Development (.env / .env.example)

- **Environment**: `dev`
- **Log Level**: `DEBUG`
- **Log Format**: `text` (human-readable)
- **Rate Limit**: 60 requests/minute
- **Provider**: Ollama (local, no API key needed)

**Best for**: Local development and testing

### Production (.env.production)

- **Environment**: `prod`
- **Log Level**: `INFO`
- **Log Format**: `json` (for log aggregation)
- **Rate Limit**: 50 requests/minute (conservative)
- **Provider**: Gemini (or your preferred cloud provider)

**Best for**: Production deployments

### Test (.env.test)

- **Environment**: `test`
- **Log Level**: `WARNING`
- **Log Format**: `text`
- **Rate Limit**: 100 requests/minute
- **Provider**: Ollama (local) or mock providers

**Best for**: Running test suites

## Configuration Options

### LLM Provider

Choose your LLM provider by setting `LLM_PROVIDER`:

- **`ollama`** - Local LLM (no API key, requires Ollama installed)
- **`gemini`** - Google Gemini (requires `GEMINI_API_KEY`)
- **`openai`** - OpenAI GPT (requires `OPENAI_API_KEY`)

### Ollama Configuration

```env
OLLAMA_DEFAULT_MODEL=dolphin3
OLLAMA_BASE_URL=http://localhost:11434
```

**Setup**:
1. Install Ollama: https://ollama.ai
2. Start Ollama: `ollama serve`
3. Pull a model: `ollama pull dolphin3`

### Gemini Configuration

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Get API Key**: https://aistudio.google.com/app/apikey

### OpenAI Configuration

```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Get API Key**: https://platform.openai.com/api-keys

### Logging Configuration

```env
LOG_LEVEL=DEBUG          # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=text          # text or json
LOG_DIR=logs             # Log directory
```

### Application Configuration

```env
DOCS_DIR=docs                    # Documentation output directory
RATE_LIMIT_PER_MINUTE=60         # API rate limit
```

## Troubleshooting

### Error: `AttributeError: module 'google' has no attribute 'generativeai'`

This error occurs when:
1. The `google-generativeai` package is not installed
2. You're using the wrong Python environment
3. There's a conflicting `google` package

**Solution**:
```bash
# Make sure you're using the virtual environment
source .venv/bin/activate

# Or use uv run
uv run python your_script.py

# Reinstall dependencies
uv sync --all-extras

# Or with pip
pip install google-generativeai
```

### Error: Cannot connect to Ollama

**Solution**:
```bash
# Check if Ollama is running
ollama serve

# Verify the model is available
ollama list

# Pull the model if needed
ollama pull dolphin3
```

### Error: API key not found

**Solution**:
1. Check that your `.env` file exists
2. Verify the API key is set correctly (no quotes, no spaces)
3. Make sure you're loading the `.env` file (the app uses `python-dotenv`)

## Security Notes

- **Never commit** `.env`, `.env.production`, or `.env.test` to version control
- `.env.example` is safe to commit (contains no secrets)
- Use environment variables or secrets management in production
- Rotate API keys regularly
- Use different API keys for development and production

## Examples

### Development with Ollama

```env
ENVIRONMENT=dev
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=dolphin3
OLLAMA_BASE_URL=http://localhost:11434
```

### Production with Gemini

```env
ENVIRONMENT=prod
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_production_key_here
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_PER_MINUTE=50
```

### Testing

```env
ENVIRONMENT=test
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=dolphin3
LOG_LEVEL=WARNING
DOCS_DIR=docs/test
```

