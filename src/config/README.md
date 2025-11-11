# Configuration Guide

## Environment Modes

This project supports three environment modes: **DEV**, **PROD**, and **TEST**.

### Setting Environment

#### Method 1: Environment Variable (Recommended)
```bash
# Development mode
export ENVIRONMENT=dev
python -m src.web.app

# Production mode
export ENVIRONMENT=prod
python -m src.web.app
```

#### Method 2: Python Code
```python
from src.config import set_environment, Environment

# Set to DEV mode
set_environment(Environment.DEV)

# Set to PROD mode
set_environment(Environment.PROD)
```

#### Method 3: .env File
Create a `.env` file:
```env
ENVIRONMENT=dev
# or
ENVIRONMENT=prod
```

## Environment Differences

### DEV Mode
- **Log Format**: Text (human-readable)
- **Log Level**: DEBUG
- **Performance Logging**: Enabled
- **Profiling**: Enabled
- **Verbose Output**: True
- **Rate Limit**: 60 requests/minute

### PROD Mode
- **Log Format**: JSON (for log analysis tools)
- **Log Level**: INFO
- **Performance Logging**: Enabled
- **Profiling**: Disabled (performance overhead)
- **Verbose Output**: False
- **Rate Limit**: 60 requests/minute (configurable)

### TEST Mode
- **Log Format**: Text
- **Log Level**: WARNING
- **Performance Logging**: Disabled
- **Profiling**: Disabled
- **Verbose Output**: False
- **Rate Limit**: 100 requests/minute

## Configuration Options

All settings can be overridden via environment variables:

```bash
# Logging
export LOG_LEVEL=DEBUG
export LOG_FORMAT=json  # or 'text'
export LOG_DIR=logs

# LLM Provider Configuration
export LLM_PROVIDER=gemini  # Options: gemini, ollama, openai
export RATE_LIMIT_PER_MINUTE=60

# Gemini Configuration (if LLM_PROVIDER=gemini)
export GEMINI_API_KEY=your_gemini_api_key_here
export GEMINI_DEFAULT_MODEL=gemini-2.0-flash  # Optional

# Ollama Configuration (if LLM_PROVIDER=ollama)
export OLLAMA_BASE_URL=http://localhost:11434  # Optional
export OLLAMA_MODEL=dolphin3  # Optional

# OpenAI Configuration (if LLM_PROVIDER=openai)
export OPENAI_API_KEY=your_openai_api_key_here
export OPENAI_MODEL=gpt-4o-mini  # Optional

# Directories
export DOCS_DIR=docs
```

## Usage Examples

### Using Performance Monitoring

```python
from src.utils.performance import track_performance, PerformanceMonitor

# Decorator approach
@track_performance(min_time_ms=100, log_level='INFO')
def slow_operation():
    # Your code here
    pass

# Context manager approach
with PerformanceMonitor("document_generation"):
    # Your code here
    generate_documents()
```

### Checking Environment

```python
from src.config import is_dev, is_prod, get_environment

if is_dev():
    print("Running in development mode")
    # Add debug code here

if is_prod():
    print("Running in production mode")
    # Production-specific logic

env = get_environment()
print(f"Current environment: {env.value}")
```

## Log Format Examples

### DEV Mode (Text Format)
```
2024-01-15 10:30:45 | INFO     | src.agents.base_agent | _call_llm:124 | RequirementsAnalyst LLM call completed (response length: 1234 characters)
```

### PROD Mode (JSON Format)
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "level": "INFO",
  "logger": "src.agents.base_agent",
  "message": "RequirementsAnalyst LLM call completed (response length: 1234 characters)",
  "module": "base_agent",
  "function": "_call_llm",
  "line": 124,
  "execution_time_seconds": 1.234
}
```

## Best Practices

1. **Development**: Use DEV mode for debugging and development
2. **Production**: Always use PROD mode with JSON logging for log analysis
3. **Testing**: Use TEST mode to reduce log noise during tests
4. **Environment Variables**: Set environment variables in your deployment system
5. **Log Rotation**: Automatically handled (10MB per file, 5 backups)

