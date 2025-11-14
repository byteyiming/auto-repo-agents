# OmniDoc Backend Documentation

Complete guide for running and configuring the OmniDoc backend.

## 🚀 Quick Start

### Option 1: Using the Development Script (Recommended)

```bash
python3 backend/uvicorn_dev.py
```

The server will start at `http://localhost:8000` with auto-reload enabled.

### Option 2: Using uvicorn Directly

```bash
uvicorn src.web.app:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Using uv

```bash
uv run python -m uvicorn src.web.app:app --reload --host 0.0.0.0 --port 8000
```

## 📋 Prerequisites

### Required Services

1. **PostgreSQL Database**
   ```bash
   # Install PostgreSQL
   # Ubuntu/Debian:
   sudo apt-get install postgresql
   # macOS:
   brew install postgresql
   
   # Create database
   createdb omnidoc
   ```

2. **Redis** (for Celery and caching)
   ```bash
   # Install Redis
   # Ubuntu/Debian:
   sudo apt-get install redis-server
   # macOS:
   brew install redis
   
   # Start Redis
   sudo systemctl start redis  # Linux
   brew services start redis   # macOS
   ```

3. **Python 3.9+**
   ```bash
   python3 --version
   ```

## ⚙️ Environment Configuration

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/omnidoc
# Default: postgresql://localhost/omnidoc (if not set)

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# LLM Provider Configuration
LLM_PROVIDER=gemini  # Options: gemini, ollama, openai
GEMINI_API_KEY=your_api_key_here

# Document Configuration
DOCUMENT_CONFIG_PATH=config/document_definitions.json
DOCS_DIR=docs

# Web Application Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Authentication (Optional)
JWT_SECRET_KEY=your-secret-key-change-in-production
GOOGLE_CLIENT_ID=your_google_client_id
GITHUB_CLIENT_ID=your_github_client_id
```

## 🔌 API Endpoints

Once running, the API is available at `http://localhost:8000`:

### Core Endpoints

- **Document Templates**: `GET /api/document-templates`
  - Returns list of available document types
  
- **Create Project**: `POST /api/projects`
  - Creates a new documentation project
  - Returns project ID and status
  
- **Project Status**: `GET /api/projects/{project_id}/status`
  - Get current status of a project
  
- **Project Documents**: `GET /api/projects/{project_id}/documents`
  - List all generated documents for a project
  
- **Single Document**: `GET /api/projects/{project_id}/documents/{document_id}`
  - Get a specific document with content
  
- **Download Document**: `GET /api/projects/{project_id}/documents/{document_id}/download`
  - Download a document file

### WebSocket

- **Real-time Updates**: `ws://localhost:8000/ws/{project_id}`
  - Real-time progress updates for document generation

## 📖 API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔄 Background Tasks (Celery)

OmniDoc uses Celery for background task processing. You must run a Celery worker:

```bash
# Start Celery worker
./scripts/start_celery_worker.sh

# Or manually
celery -A src.tasks.celery_app worker --loglevel=info
```

### Why Celery?

- **Reliability**: Tasks survive server restarts
- **Scalability**: Run multiple workers for parallel processing
- **Monitoring**: Track task progress and status
- **Resource Management**: Better CPU and memory management

## 🗄️ Database

### Initialization

The database tables are created automatically on first run. No manual migration needed.

### Tables

- `projects` - Project metadata
- `requirements` - Requirements documents
- `agent_outputs` - Generated documents with versions
- `cross_references` - Document cross-references
- `project_status` - Workflow status tracking

### Connection

The backend uses PostgreSQL via `psycopg2`. Connection string is configured via `DATABASE_URL` environment variable.

## 💾 Caching

Redis is used for:
- **Document Templates**: Cached for 24 hours
- **Project Results**: Can be cached for faster retrieval
- **Celery Broker**: Task queue message broker

Caching is automatic and gracefully falls back if Redis is unavailable.

## 🔐 Authentication

Authentication infrastructure is in place but not yet integrated into API endpoints:

- **JWT Tokens**: Token creation and verification
- **OAuth2**: Google and GitHub provider support
- **Password Hashing**: Bcrypt-based password hashing

To enable authentication, add middleware to FastAPI routes.

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
BACKEND_PORT=8001 python3 backend/uvicorn_dev.py
```

### Database Connection Error

```bash
# Check PostgreSQL is running
pg_isready

# Verify database exists
psql -l | grep omnidoc

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

### Redis Connection Error

```bash
# Check Redis is running
redis-cli ping  # Should return PONG

# Test connection
redis-cli info
```

### Celery Worker Not Processing Tasks

```bash
# Check if Redis is running
redis-cli ping

# Check Celery worker logs
celery -A src.tasks.celery_app worker --loglevel=debug

# Check active tasks
celery -A src.tasks.celery_app inspect active
```

### Missing Dependencies

```bash
# Install dependencies
./scripts/setup.sh

# Or manually
pip install -r requirements.txt
# Or with uv
uv sync --all-extras
```

### Configuration File Not Found

```bash
# Generate document definitions from CSV
python3 scripts/csv_to_document_json.py \
  --input JobTrackrAI_Document_Management_Template_v3.csv \
  --output config/document_definitions.json
```

## 📊 Monitoring

### Check Service Status

```bash
# PostgreSQL
pg_isready

# Redis
redis-cli ping

# Celery
celery -A src.tasks.celery_app inspect active
```

### View Logs

```bash
# Backend logs
tail -f logs/app.log

# Celery worker logs
# (shown in terminal where worker is running)
```

## 🔧 Development

### Running Tests

```bash
# All tests
pytest

# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration
```

### Code Quality

```bash
# Format
black src tests

# Lint
ruff check src tests
```

## 📚 Additional Resources

- **Main README**: [README.md](README.md)
- **Production Setup**: [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md)
- **Production Improvements**: [README_PRODUCTION.md](README_PRODUCTION.md)
- **Documentation Index**: [DOCS_INDEX.md](DOCS_INDEX.md)
