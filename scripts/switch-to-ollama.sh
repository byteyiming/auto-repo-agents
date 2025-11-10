#!/bin/bash
# 快速切换到 Ollama 提供商

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔄 切换到 Ollama 提供商..."

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo "❌ .env 文件不存在，正在从 .env.example 创建..."
    cp .env.example .env
fi

# 备份 .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# 更新 LLM_PROVIDER
if grep -q "^LLM_PROVIDER=" .env; then
    sed -i.bak 's/^LLM_PROVIDER=.*/LLM_PROVIDER=ollama/' .env
else
    echo "LLM_PROVIDER=ollama" >> .env
fi

# 确保 Ollama 配置存在
if ! grep -q "^OLLAMA_DEFAULT_MODEL=" .env; then
    echo "OLLAMA_DEFAULT_MODEL=dolphin3" >> .env
fi

if ! grep -q "^OLLAMA_BASE_URL=" .env; then
    echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
fi

if ! grep -q "^OLLAMA_MAX_TOKENS=" .env; then
    echo "OLLAMA_MAX_TOKENS=8192" >> .env
fi

# 注释掉 Gemini API Key（如果存在）
if grep -q "^GEMINI_API_KEY=" .env; then
    sed -i.bak 's/^GEMINI_API_KEY=/# GEMINI_API_KEY=/' .env
fi

# 清理备份文件
rm -f .env.bak

echo "✅ 已切换到 Ollama"
echo ""
echo "📋 当前配置："
grep -E "^(LLM_PROVIDER|OLLAMA_)" .env | grep -v "^#"
echo ""
echo "⚠️  请确保："
echo "   1. Ollama 服务正在运行: ollama serve"
echo "   2. 模型已下载: ollama pull dolphin3"
echo "   3. 验证连接: curl http://localhost:11434/api/tags"
