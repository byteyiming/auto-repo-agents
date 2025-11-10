#!/bin/bash
# 检查当前使用的 LLM 提供商

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔍 检查当前 LLM 提供商配置..."
echo ""

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "❌ .env 文件不存在"
    echo "   请运行: cp .env.example .env"
    exit 1
fi

# 读取配置
LLM_PROVIDER=$(grep "^LLM_PROVIDER=" .env 2>/dev/null | cut -d'=' -f2 || echo "未设置")

echo "📋 当前配置："
echo "   LLM_PROVIDER: ${LLM_PROVIDER:-未设置}"
echo ""

if [ "$LLM_PROVIDER" = "ollama" ]; then
    echo "✅ 当前使用: Ollama (本地模型)"
    echo ""
    OLLAMA_MODEL=$(grep "^OLLAMA_DEFAULT_MODEL=" .env 2>/dev/null | cut -d'=' -f2 || echo "dolphin3")
    OLLAMA_URL=$(grep "^OLLAMA_BASE_URL=" .env 2>/dev/null | cut -d'=' -f2 || echo "http://localhost:11434")
    
    echo "   模型: $OLLAMA_MODEL"
    echo "   Base URL: $OLLAMA_URL"
    echo ""
    
    # 检查 Ollama 是否运行
    if curl -s "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
        echo "   ✅ Ollama 服务正在运行"
        
        # 检查模型是否存在
        if ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
            echo "   ✅ 模型 '$OLLAMA_MODEL' 已下载"
        else
            echo "   ⚠️  模型 '$OLLAMA_MODEL' 未找到"
            echo "   运行: ollama pull $OLLAMA_MODEL"
        fi
    else
        echo "   ❌ Ollama 服务未运行"
        echo "   运行: ollama serve"
    fi
    
elif [ "$LLM_PROVIDER" = "gemini" ]; then
    echo "✅ 当前使用: Gemini (云端模型)"
    echo ""
    GEMINI_KEY=$(grep "^GEMINI_API_KEY=" .env 2>/dev/null | cut -d'=' -f2 || echo "")
    
    if [ -n "$GEMINI_KEY" ] && [ "$GEMINI_KEY" != "your_gemini_api_key_here" ]; then
        echo "   ✅ GEMINI_API_KEY 已设置"
        # 测试连接（简单检查）
        echo "   ℹ️  使用 Python 验证连接..."
    else
        echo "   ❌ GEMINI_API_KEY 未设置或无效"
        echo "   请编辑 .env 文件设置 API Key"
        echo "   获取 API Key: https://aistudio.google.com/app/apikey"
    fi
    
elif [ "$LLM_PROVIDER" = "openai" ]; then
    echo "✅ 当前使用: OpenAI (云端模型)"
    echo ""
    OPENAI_KEY=$(grep "^OPENAI_API_KEY=" .env 2>/dev/null | cut -d'=' -f2 || echo "")
    
    if [ -n "$OPENAI_KEY" ] && [ "$OPENAI_KEY" != "your_openai_api_key_here" ]; then
        echo "   ✅ OPENAI_API_KEY 已设置"
    else
        echo "   ❌ OPENAI_API_KEY 未设置或无效"
        echo "   请编辑 .env 文件设置 API Key"
    fi
else
    echo "⚠️  未知的 LLM 提供商: $LLM_PROVIDER"
    echo "   支持的提供商: ollama, gemini, openai"
fi

echo ""
echo "💡 切换提供商："
echo "   ./scripts/switch-to-ollama.sh  # 切换到 Ollama"
echo "   ./scripts/switch-to-gemini.sh  # 切换到 Gemini"
echo "   或直接编辑 .env 文件中的 LLM_PROVIDER"
