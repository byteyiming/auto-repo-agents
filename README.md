# OmniDoc (DOCU-GEN)

AI-powered documentation generation system that creates comprehensive documentation from simple user ideas using multi-agent collaboration. Supports multiple LLM providers including Gemini, OpenAI, and **Ollama (local LLM)**.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd OmniDoc

# Run setup script (uses uv to sync from pyproject.toml)
./scripts/setup.sh
```

The setup script will:
- Create a virtual environment (`.venv`)
- Install all dependencies from `pyproject.toml`
- Verify installation and Ollama provider setup
- Support both `uv` (recommended) and `pip` fallback

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and configure your LLM provider
# Options: Ollama (local, no API key), Gemini, or OpenAI
```

**For Ollama (Recommended for Development):**
```bash
# In .env file
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=dolphin3
OLLAMA_BASE_URL=http://localhost:11434

# Make sure Ollama is running
ollama serve

# Pull the model
ollama pull dolphin3
```

**For Gemini:**
```bash
# In .env file
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
```

**For OpenAI:**
```bash
# In .env file
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Generate Documentation

```bash
# Using CLI
uv run python -c "
from src.coordination.coordinator import WorkflowCoordinator
coordinator = WorkflowCoordinator()
coordinator.generate_all_docs('Build a task management app')
"

# Or use web interface
uv run python -m src.web.app
# Visit http://localhost:8000
```

## 📋 Features

### Core Capabilities

- **20+ Documentation Agents**: Requirements, PM, Technical, API, Developer, Stakeholder, User, Test, Quality Review, Format Converter, Business Model, Marketing Plan, Legal Compliance, Database Schema, Setup Guide, User Stories, Support Playbook, and more
- **Multi-LLM Support**: 
  - **Ollama** (local, no API key required) - Recommended for development
  - **Google Gemini** (cloud-based)
  - **OpenAI GPT** (cloud-based)
  - Extensible architecture for other providers
- **Format Conversion**: Outputs Markdown, HTML, PDF, DOCX
- **Quality Assurance**: Automated quality checks and scoring
- **Parallel Execution**: 3x speedup for independent agents
- **Web Interface**: FastAPI web app with real-time progress tracking
- **Error Handling**: Retry logic with exponential backoff
- **Document Templates**: Jinja2-based customizable templates
- **Cross-Referencing**: Automatic linking between documents
- **Intelligent Parsing**: Structured data extraction from requirements
- **Context Management**: SQLite-based shared context across agents
- **Rate Limiting**: Built-in rate limiting and caching

### LLM Provider Features

- **Ollama Provider**: 
  - Local LLM support (no API costs)
  - Configurable token limits (default: 8192 tokens)
  - Supports all Ollama models (dolphin3, llama2, mistral, etc.)
  - Automatic connection handling
- **Gemini Provider**:
  - Rate limit handling with automatic retry
  - Support for multiple Gemini models
- **OpenAI Provider**:
  - Full GPT-4 and GPT-3.5 support
  - Configurable models and parameters

## 🏗️ Project Structure

```
OmniDoc/
├── src/                    # Source code
│   ├── agents/            # Documentation agents (20+ agents)
│   ├── context/           # Shared context management (SQLite)
│   ├── coordination/      # Workflow orchestration
│   ├── llm/               # LLM provider abstractions
│   │   ├── base_provider.py
│   │   ├── ollama_provider.py    # Ollama local LLM
│   │   ├── gemini_provider.py    # Google Gemini
│   │   ├── openai_provider.py    # OpenAI GPT
│   │   └── provider_factory.py
│   ├── quality/           # Quality checking
│   ├── rate_limit/        # Rate limiting & caching
│   ├── utils/             # Utilities (parsers, templates, etc.)
│   └── web/               # Web interface (FastAPI)
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
├── docs/                  # Generated documentation
├── templates/             # Document templates (Jinja2)
├── prompts/               # System prompts (editable)
├── scripts/               # Setup and utility scripts
│   ├── setup.sh           # Main setup script
│   ├── use-env.sh         # Environment switcher
│   └── fix-google-import.sh  # Import fixer
├── .env.example           # Environment template
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

See [ENV_SETUP.md](ENV_SETUP.md) for detailed configuration guide.

**Key Configuration Options:**
- `LLM_PROVIDER`: Choose provider (ollama, gemini, openai)
- `OLLAMA_DEFAULT_MODEL`: Model name for Ollama (default: dolphin3)
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MAX_TOKENS`: Max output tokens for Ollama (default: 8192)
- `GEMINI_API_KEY`: Gemini API key (if using Gemini)
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI)
- `ENVIRONMENT`: Environment mode (dev, prod, test)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `DOCS_DIR`: Output directory for generated docs

### Switching Environments

```bash
# Switch to development environment
./scripts/use-env.sh dev

# Switch to production environment
./scripts/use-env.sh prod

# Switch to test environment
./scripts/use-env.sh test
```

## 📚 Documentation

- **Environment Setup**: See [ENV_SETUP.md](ENV_SETUP.md) for environment configuration
- **Ollama Token Fix**: See [OLLAMA_TOKEN_FIX.md](OLLAMA_TOKEN_FIX.md) for token limit configuration
- **Current Status**: See [CURRENT_STATUS.md](CURRENT_STATUS.md) for project status
- **Generated Docs**: See [docs/README.md](docs/README.md) for generated documentation index
- **Config Guide**: See [src/config/README.md](src/config/README.md) for configuration details

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Unit tests only (fast)
uv run pytest tests/unit

# Integration tests
uv run pytest tests/integration

# E2E tests (requires API key or Ollama)
uv run pytest tests/e2e

# With coverage
uv run pytest --cov=src --cov-report=html
```

**Current Status:** 100+ tests, 82% code coverage

## 🎯 Usage Examples

### Generate All Documentation

```bash
# Using CLI
uv run python -c "
from src.coordination.coordinator import WorkflowCoordinator
coordinator = WorkflowCoordinator()
results = coordinator.generate_all_docs('Build a blog platform with user authentication')
"
```

Or in a Python script:
```python
from src.coordination.coordinator import WorkflowCoordinator

coordinator = WorkflowCoordinator()
results = coordinator.generate_all_docs(
    "Build a blog platform with user authentication"
)

# Generates 20+ document types:
# - Requirements
# - Project Charter
# - Business Model
# - Marketing Plan
# - PM Plan
# - User Stories
# - Technical Spec
# - API Documentation
# - Database Schema
# - Developer Guide
# - Setup Guide
# - Stakeholder Summary
# - User Guide
# - Test Plan
# - Legal Compliance
# - Support Playbook
# - Quality Review
# - Format conversions (HTML, PDF, DOCX)
```

### Use Web Interface

```bash
# Start the web server
uv run python -m src.web.app

# Visit http://localhost:8000
# Enter your project idea and generate docs!
```

### Switch LLM Provider

#### Method 1: Edit .env File (Recommended)

```bash
# Edit .env file
nano .env

# For Ollama (local)
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=dolphin3

# For Gemini (cloud)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
```

#### Method 2: Use Switch Scripts

```bash
# Switch to Ollama
./scripts/switch-to-ollama.sh

# Switch to Gemini
./scripts/switch-to-gemini.sh

# Check current provider
./scripts/check-llm-provider.sh
```

#### Method 3: In Code

```python
# Use Ollama (local)
from src.agents.requirements_analyst import RequirementsAnalyst

agent = RequirementsAnalyst(provider_name="ollama")

# Use Gemini (cloud)
agent = RequirementsAnalyst(provider_name="gemini")

# Use OpenAI (cloud)
agent = RequirementsAnalyst(provider_name="openai")
```

**See [SWITCH_LLM_PROVIDER.md](SWITCH_LLM_PROVIDER.md) for detailed switching guide.**

### Multiple Provider Example

See [examples/multi_provider_example.py](examples/multi_provider_example.py) for examples of using different providers.

## 🛠️ Development

### Setup Development Environment

```bash
# Install with dev dependencies
uv sync --all-extras

# Or use setup script
./scripts/setup.sh
```

### Running the Application

```bash
# Activate virtual environment (if not using uv run)
source .venv/bin/activate

# Or use uv run (recommended)
uv run python -m src.web.app
```

### Code Quality

```bash
# Format code
uv run black src tests

# Lint code
uv run ruff check src tests

# Type checking (if using mypy)
uv run mypy src
```

## 🔍 Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
ollama serve

# Verify model is available
ollama list

# Pull the model if needed
ollama pull dolphin3
```

### Google GenerativeAI Import Error

```bash
# Run the fix script
./scripts/fix-google-import.sh

# Or manually fix
pip uninstall google -y
pip install google-generativeai
```

### Environment Configuration

See [ENV_SETUP.md](ENV_SETUP.md) for detailed troubleshooting guide.

## 📦 Dependencies

### Core Dependencies
- `google-generativeai>=0.3.0` - Gemini provider
- `requests>=2.31.0` - HTTP client (for Ollama)
- `fastapi>=0.100.0` - Web framework
- `uvicorn>=0.23.0` - ASGI server
- `python-dotenv>=1.0.0` - Environment variables
- `jinja2>=3.1.2` - Template engine
- `pydantic>=2.0.0` - Data validation
- `markdown>=3.5.0` - Markdown processing
- `weasyprint>=60.0` - PDF generation
- `python-docx>=1.1.0` - DOCX generation

### Optional Dependencies
- `openai>=1.0.0` - OpenAI provider (install with `uv sync --extra openai`)
- `anthropic>=0.18.0` - Anthropic provider (install with `uv sync --extra anthropic`)

See [pyproject.toml](pyproject.toml) for complete dependency list.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `uv run pytest`
5. Submit a pull request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with multi-agent collaboration
- Supports multiple LLM providers for flexibility
- Designed for comprehensive documentation generation

## 🔗 Related Documentation

- [Environment Setup Guide](ENV_SETUP.md)
- [Switch LLM Provider Guide](SWITCH_LLM_PROVIDER.md) - How to switch between Gemini and Ollama
- [Ollama Token Fix Documentation](OLLAMA_TOKEN_FIX.md)
- [Quality Scores Analysis](QUALITY_SCORES_ANALYSIS.md)
- [Configuration Guide](src/config/README.md)
- [Current Project Status](CURRENT_STATUS.md)

---

**Note:** This project uses `uv` to manage dependencies from `pyproject.toml`. 
- Use `uv run <command>` to run commands in the project environment
- No need to activate virtual environment manually
- Dependencies are managed via `pyproject.toml`
