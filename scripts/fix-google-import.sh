#!/bin/bash
# Fix script for google-generativeai import errors
# This error occurs when there's a conflicting 'google' package

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🔧 Fixing google-generativeai import issue..."
echo ""

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ] && [ ! -d ".venv" ]; then
    echo "❌ No virtual environment found"
    echo "Please run: ./scripts/setup.sh"
    exit 1
fi

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

echo "🔍 Checking for conflicting google packages..."
python3 -c "
import sys
try:
    import google
    print(f'Found google module at: {google.__file__}')
    print(f'Google module contents: {dir(google)}')
    
    # Check if it's the wrong google package
    if 'generativeai' not in dir(google):
        print('⚠️  WARNING: google module exists but generativeai is missing!')
        print('This is likely a conflicting package.')
        print('')
        print('Solution:')
        print('1. Uninstall the conflicting google package:')
        print('   pip uninstall google -y')
        print('2. Install google-generativeai:')
        print('   pip install google-generativeai')
        sys.exit(1)
    else:
        print('✅ google-generativeai is properly installed')
except ImportError:
    print('❌ google module not found')
    print('Installing google-generativeai...')
    sys.exit(2)
" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 1 ]; then
    echo ""
    echo "🔧 Fixing the issue..."
    echo ""
    echo "Uninstalling conflicting packages..."
    pip uninstall google -y 2>/dev/null || true
    pip uninstall google-generativeai -y 2>/dev/null || true
    
    echo "Installing google-generativeai..."
    pip install google-generativeai>=0.3.0
    
    echo ""
    echo "✅ Fixed! Try running your script again."
elif [ $EXIT_CODE -eq 2 ]; then
    echo ""
    echo "Installing google-generativeai..."
    pip install google-generativeai>=0.3.0
    echo "✅ Installed! Try running your script again."
else
    echo "✅ No issues found!"
fi

echo ""
echo "💡 Note: If you're using Ollama, you don't need google-generativeai."
echo "   Make sure LLM_PROVIDER=ollama in your .env file."
