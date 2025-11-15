#!/bin/bash
# Database Initialization Script
# Creates all database tables for OmniDoc
# Usage: ./scripts/init_database.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

echo -e "${BLUE}🗄️  OmniDoc Database Initialization${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Please run ./scripts/setup.sh first to create .env file"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Check DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ DATABASE_URL not set in .env file${NC}"
    echo "Please set DATABASE_URL in .env file"
    exit 1
fi

echo -e "${GREEN}📋 Database URL: ${DATABASE_URL}${NC}"
echo ""

# Check if Python virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "Please run ./scripts/setup.sh first"
    exit 1
fi

# Check if uv is available
if command -v uv &> /dev/null; then
    USE_UV=true
else
    USE_UV=false
fi

echo -e "${BLUE}🔧 Initializing database tables...${NC}"
echo ""

# Run Python script to initialize database
if [ "$USE_UV" = true ]; then
    uv run python << 'PYTHON_EOF'
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import ContextManager
from src.context.context_manager import ContextManager

print("Connecting to database...")
try:
    # Initialize ContextManager which will create tables
    context = ContextManager()
    print("✅ Database tables initialized successfully!")
    print("")
    print("Created tables:")
    print("  - projects")
    print("  - requirements")
    print("  - agent_outputs")
    print("  - cross_references")
    print("  - project_status")
    print("")
    print("✅ Database initialization complete!")
except Exception as e:
    print(f"❌ Error initializing database: {e}")
    sys.exit(1)
PYTHON_EOF
else
    source .venv/bin/activate
    python << 'PYTHON_EOF'
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import ContextManager
from src.context.context_manager import ContextManager

print("Connecting to database...")
try:
    # Initialize ContextManager which will create tables
    context = ContextManager()
    print("✅ Database tables initialized successfully!")
    print("")
    print("Created tables:")
    print("  - projects")
    print("  - requirements")
    print("  - agent_outputs")
    print("  - cross_references")
    print("  - project_status")
    print("")
    print("✅ Database initialization complete!")
except Exception as e:
    print(f"❌ Error initializing database: {e}")
    sys.exit(1)
PYTHON_EOF
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database initialization successful!${NC}"
    echo ""
    echo "You can now start the application:"
    echo "  python backend/uvicorn_dev.py"
else
    echo -e "${RED}❌ Database initialization failed${NC}"
    exit 1
fi

