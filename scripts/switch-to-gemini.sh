#!/bin/bash
# 快速切换到 Gemini 提供商

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔄 切换到 Gemini 提供商..."

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo "❌ .env 文件不存在，正在从 .env.example 创建..."
    cp .env.example .env
fi

# 备份 .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# 更新 LLM_PROVIDER
if grep -q "^LLM_PROVIDER=" .env; then
    sed -i.bak 's/^LLM_PROVIDER=.*/LLM_PROVIDER=gemini/' .env
else
    echo "LLM_PROVIDER=gemini" >> .env
fi

# 检查 API Key
if ! grep -q "^GEMINI_API_KEY=" .env || grep -q "^# GEMINI_API_KEY=" .env; then
    echo ""
    echo "⚠️  警告: GEMINI_API_KEY 未设置或已注释"
    echo "   请编辑 .env 文件并设置:"
    echo "   GEMINI_API_KEY=your_gemini_api_key_here"
    echo ""
    echo "   获取 API Key: https://aistudio.google.com/app/apikey"
    echo ""
    
    # 添加占位符
    if ! grep -q "GEMINI_API_KEY" .env; then
        echo "# GEMINI_API_KEY=your_gemini_api_key_here" >> .env
    fi
fi

# 注释掉 Ollama 配置（可选，保留以便切换回来）
# sed -i.bak 's/^OLLAMA_DEFAULT_MODEL=/# OLLAMA_DEFAULT_MODEL=/' .env
# sed -i.bak 's/^OLLAMA_BASE_URL=/# OLLAMA_BASE_URL=/' .env

# 清理备份文件
rm -f .env.bak

echo "✅ 已切换到 Gemini"
echo ""
echo "📋 当前配置："
grep -E "^(LLM_PROVIDER|GEMINI_API_KEY)" .env | head -2
echo ""
echo "⚠️  请确保："
echo "   1. GEMINI_API_KEY 已在 .env 中设置"
echo "   2. API Key 有效且未过期"
echo "   3. 有足够的 API 配额"
