import ollama

# 使用 ollama.Client() 连接本地运行的服务
client = ollama.Client()

# 运行一个模型并获取回复
try:
    # 确保你已经通过命令行运行过 ollama run llama3.1 
    # 或者 ollama run mistral 来下载了模型

    stream = client.chat(
        model='llama3.1',
        messages=[{'role': 'user', 'content': '给我一个关于使用 Python 和 Ollama 的简短教程。'}],
        stream=True, # 使用流式传输可以实时看到回复
    )

    print("AI 回复：")
    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)

except Exception as e:
    print(f"发生错误: {e}")
    print("请确保 Ollama 服务正在运行，并且模型已经下载（使用 'ollama run llama3.1' 命令）")

