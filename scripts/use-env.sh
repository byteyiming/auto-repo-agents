#!/bin/bash
# Helper script to switch between environment configurations
# Usage: ./scripts/use-env.sh [dev|prod|test]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ENV_TYPE="${1:-dev}"

cd "$PROJECT_ROOT"

case "$ENV_TYPE" in
    dev|development)
        if [ -f ".env" ]; then
            echo "✅ Using existing .env file (development)"
        else
            echo "📝 Creating .env from .env.example..."
            cp .env.example .env
            echo "✅ Created .env file for development"
        fi
        ;;
    prod|production)
        if [ -f ".env.production" ]; then
            echo "📝 Copying .env.production to .env..."
            cp .env.production .env
            echo "✅ Switched to production environment"
            echo "⚠️  Remember to set your production API keys in .env"
        else
            echo "❌ .env.production not found"
            exit 1
        fi
        ;;
    test)
        if [ -f ".env.test" ]; then
            echo "📝 Copying .env.test to .env..."
            cp .env.test .env
            echo "✅ Switched to test environment"
        else
            echo "❌ .env.test not found"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 [dev|prod|test]"
        echo ""
        echo "Options:"
        echo "  dev   - Development environment (default)"
        echo "  prod  - Production environment"
        echo "  test  - Test environment"
        exit 1
        ;;
esac

echo ""
echo "Current environment configuration:"
echo "  ENVIRONMENT=$(grep '^ENVIRONMENT=' .env | cut -d'=' -f2 || echo 'not set')"
echo "  LLM_PROVIDER=$(grep '^LLM_PROVIDER=' .env | cut -d'=' -f2 || echo 'not set')"
echo ""

