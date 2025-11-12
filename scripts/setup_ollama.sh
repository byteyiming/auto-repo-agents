#!/bin/bash
# Ollama 快速设置脚本

echo "🚀 Ollama 设置向导"
echo ""

# 检查 Ollama 是否安装
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama 未安装"
    echo ""
    echo "请先安装 Ollama:"
    echo "  macOS:   brew install ollama"
    echo "  Linux:   curl -fsSL https://ollama.ai/install.sh | sh"
    echo "  Windows: 从 https://ollama.ai/download 下载"
    exit 1
fi

echo "✅ Ollama 已安装: $(ollama --version)"

# 检查服务是否运行
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama 服务正在运行"
else
    echo "⚠️  Ollama 服务未运行，正在启动..."
    ollama serve &
    sleep 2
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama 服务已启动"
    else
        echo "❌ 无法启动 Ollama 服务"
        exit 1
    fi
fi

# 获取已安装的模型
echo ""
echo "📦 检查已安装的模型..."
models=$(ollama list | tail -n +2 | awk '{print $1}' | grep -v "^$")

if [ -z "$models" ]; then
    echo "⚠️  没有安装任何模型"
    echo ""
    echo "推荐下载以下模型之一:"
    echo "  1. dolphin3 (快速，4.9GB) - 推荐用于开发"
    echo "  2. mixtral (高质量，26GB) - 推荐用于生产"
    echo ""
    read -p "是否下载 dolphin3? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 正在下载 dolphin3（这可能需要几分钟）..."
        ollama pull dolphin3
    fi
else
    echo "✅ 已安装的模型:"
    echo "$models" | while read model; do
        echo "   - $model"
    done
fi

# 更新 .env 文件
echo ""
echo "📝 更新 .env 文件..."

if [ ! -f .env ]; then
    echo "创建 .env 文件..."
    cp .env.example .env 2>/dev/null || touch .env
fi

# 获取第一个模型名称（去掉 :latest）
first_model=$(ollama list | tail -n +2 | head -1 | awk '{print $1}' | cut -d: -f1)

if [ -n "$first_model" ]; then
    # 更新或添加 OLLAMA_DEFAULT_MODEL
    if grep -q "OLLAMA_DEFAULT_MODEL" .env; then
        sed -i.bak "s/OLLAMA_DEFAULT_MODEL=.*/OLLAMA_DEFAULT_MODEL=$first_model/" .env
        echo "✅ 已更新 OLLAMA_DEFAULT_MODEL=$first_model"
    else
        echo "" >> .env
        echo "# Ollama Configuration" >> .env
        echo "OLLAMA_DEFAULT_MODEL=$first_model" >> .env
        echo "✅ 已添加 OLLAMA_DEFAULT_MODEL=$first_model"
    fi
    
    # 确保 LLM_PROVIDER=ollama
    if grep -q "LLM_PROVIDER" .env; then
        sed -i.bak "s/LLM_PROVIDER=.*/LLM_PROVIDER=ollama/" .env
    else
        echo "LLM_PROVIDER=ollama" >> .env
    fi
    echo "✅ 已设置 LLM_PROVIDER=ollama"
fi

echo ""
echo "✅ 设置完成！"
echo ""
echo "💡 使用提示:"
echo "   1. 运行测试: python test_ollama_simple.py"
echo "   2. 运行项目: python -m src.web.app"
echo "   3. 查看模型: ollama list"
echo "   4. 下载新模型: ollama pull <model_name>"
