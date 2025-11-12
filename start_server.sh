#!/bin/bash
# 启动 Web 服务器脚本

cd "$(dirname "$0")/.."

echo "🚀 启动 DOCU-GEN Web 服务器..."
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装"
    exit 1
fi

# 检查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  端口 8000 已被占用"
    echo "   正在运行的进程:"
    lsof -ti:8000 | xargs ps -p
    echo ""
    read -p "是否要停止现有进程并重新启动? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 停止现有进程..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null
        sleep 2
    else
        echo "❌ 取消启动"
        exit 1
    fi
fi

# 启动服务器
echo "✅ 启动服务器在 http://localhost:8000"
echo "   按 Ctrl+C 停止服务器"
echo ""

python3 -m uvicorn src.web.app:app --reload --host 0.0.0.0 --port 8000

