#!/usr/bin/env python3
"""
快速测试 Ollama 本地连接
"""
import os
import sys

# 设置环境变量
os.environ['LLM_PROVIDER'] = 'ollama'
os.environ['OLLAMA_DEFAULT_MODEL'] = 'mistral'  # 使用你已安装的模型
os.environ['OLLAMA_MAX_TOKENS'] = '8192'

try:
    from src.llm.ollama_provider import OllamaProvider
    
    print("🔍 测试 Ollama 连接...")
    provider = OllamaProvider()
    
    # 测试连接
    if provider.validate_config():
        print("✅ Ollama 服务连接成功！")
        print(f"   服务地址: {provider.base_url}")
        print(f"   默认模型: {provider.default_model_name}")
        
        # 测试生成
        print("\n🧪 测试文本生成...")
        test_prompt = "用一句话介绍 Python 编程语言"
        result = provider.generate(test_prompt, temperature=0.7)
        print(f"✅ 生成成功！")
        print(f"   提示: {test_prompt}")
        print(f"   回复: {result[:100]}...")
        
        print("\n✅ 所有测试通过！Ollama 可以正常使用。")
    else:
        print("❌ Ollama 服务连接失败")
        print("   请确保：")
        print("   1. Ollama 服务正在运行: ollama serve")
        print("   2. 模型已下载: ollama pull dolphin3")
        print("   3. 服务地址正确: http://localhost:11434")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("   请确保已安装项目依赖: pip install -e .")
    sys.exit(1)
except Exception as e:
    print(f"❌ 错误: {e}")
    sys.exit(1)
