#!/usr/bin/env python3
"""简单测试 Ollama 连接"""
import requests

try:
    # 测试 Ollama API 连接
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    response.raise_for_status()
    
    models = response.json().get("models", [])
    print("✅ Ollama 服务正在运行！")
    print(f"\n📦 已安装的模型:")
    for model in models:
        print(f"   - {model['name']}")
    
    if models:
        print(f"\n💡 建议：在 .env 文件中设置 OLLAMA_DEFAULT_MODEL={models[0]['name'].split(':')[0]}")
    else:
        print("\n⚠️  没有安装任何模型，请运行: ollama pull dolphin3")
        
except requests.exceptions.ConnectionError:
    print("❌ 无法连接到 Ollama 服务")
    print("   请确保 Ollama 正在运行: ollama serve")
except Exception as e:
    print(f"❌ 错误: {e}")
