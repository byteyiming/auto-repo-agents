# 如何切换 LLM 提供商（Gemini / Ollama）

## 快速切换方法

### 方法一：修改 .env 文件（推荐）

编辑 `.env` 文件，修改 `LLM_PROVIDER` 变量：

#### 使用 Ollama（本地部署模型）

```bash
# 编辑 .env 文件
nano .env  # 或使用你喜欢的编辑器

# 设置以下内容：
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=dolphin3
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MAX_TOKENS=8192

# 注释掉或删除 Gemini 相关配置
# GEMINI_API_KEY=your_gemini_api_key_here
```

#### 使用 Gemini（云端模型）

```bash
# 编辑 .env 文件
nano .env

# 设置以下内容：
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here

# 注释掉或删除 Ollama 相关配置
# OLLAMA_DEFAULT_MODEL=dolphin3
# OLLAMA_BASE_URL=http://localhost:11434
```

### 方法二：使用环境切换脚本

```bash
# 切换到开发环境（使用 Ollama）
./scripts/use-env.sh dev

# 切换到生产环境（使用 Gemini）
./scripts/use-env.sh prod
```

### 方法三：在代码中指定

```python
from src.agents.requirements_analyst import RequirementsAnalyst

# 使用 Ollama
agent = RequirementsAnalyst(provider_name="ollama")

# 使用 Gemini
agent = RequirementsAnalyst(provider_name="gemini")

# 使用 OpenAI
agent = RequirementsAnalyst(provider_name="openai")
```

## 详细配置说明

### Ollama 配置（本地模型）

**优点：**
- ✅ 无需 API 密钥
- ✅ 免费使用
- ✅ 数据隐私（数据不离开本地）
- ✅ 无 API 调用限制
- ✅ 可离线使用

**缺点：**
- ⚠️ 需要本地安装 Ollama
- ⚠️ 需要足够的硬件资源（内存、GPU）
- ⚠️ 模型质量可能不如云端模型

**配置步骤：**

1. **安装 Ollama**
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # 或访问 https://ollama.ai 下载安装
   ```

2. **启动 Ollama 服务**
   ```bash
   ollama serve
   ```

3. **下载模型**
   ```bash
   # 下载推荐的模型
   ollama pull dolphin3
   
   # 或其他模型
   ollama pull llama2
   ollama pull mistral
   ollama pull codellama
   ```

4. **配置 .env 文件**
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_DEFAULT_MODEL=dolphin3
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MAX_TOKENS=8192
   ```

5. **验证配置**
   ```bash
   # 检查 Ollama 是否运行
   curl http://localhost:11434/api/tags
   
   # 查看已下载的模型
   ollama list
   ```

### Gemini 配置（云端模型）

**优点：**
- ✅ 模型质量高
- ✅ 无需本地资源
- ✅ 自动更新和维护
- ✅ 支持多种模型（gemini-2.0-flash, gemini-2.5-pro 等）

**缺点：**
- ⚠️ 需要 API 密钥
- ⚠️ 可能有 API 调用限制
- ⚠️ 数据会发送到云端
- ⚠️ 需要网络连接

**配置步骤：**

1. **获取 API 密钥**
   - 访问：https://aistudio.google.com/app/apikey
   - 登录 Google 账号
   - 创建新的 API 密钥

2. **配置 .env 文件**
   ```env
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **验证配置**
   ```bash
   # 测试 Gemini 连接
   uv run python -c "
   from src.llm.provider_factory import ProviderFactory
   provider = ProviderFactory.create('gemini')
   print(f'Provider: {provider.get_provider_name()}')
   print(f'Model: {provider.get_default_model()}')
   "
   ```

## 切换示例

### 从 Gemini 切换到 Ollama

```bash
# 1. 编辑 .env 文件
nano .env

# 2. 修改配置
# 将：
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key

# 改为：
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=dolphin3

# 3. 确保 Ollama 正在运行
ollama serve

# 4. 验证切换
uv run python -c "
from src.llm.provider_factory import ProviderFactory
provider = ProviderFactory.create()
print(f'Current provider: {provider.get_provider_name()}')
"
```

### 从 Ollama 切换到 Gemini

```bash
# 1. 编辑 .env 文件
nano .env

# 2. 修改配置
# 将：
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=dolphin3

# 改为：
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here

# 3. 验证切换
uv run python -c "
from src.llm.provider_factory import ProviderFactory
provider = ProviderFactory.create()
print(f'Current provider: {provider.get_provider_name()}')
"
```

## 快速切换脚本

创建一个快速切换脚本：

```bash
# 创建切换脚本
cat > switch_to_ollama.sh << 'EOF'
#!/bin/bash
# 切换到 Ollama

# 备份当前 .env
cp .env .env.backup

# 更新配置
sed -i.bak 's/^LLM_PROVIDER=.*/LLM_PROVIDER=ollama/' .env
sed -i.bak 's/^# OLLAMA_DEFAULT_MODEL/OLLAMA_DEFAULT_MODEL/' .env

# 注释掉 Gemini
sed -i.bak 's/^GEMINI_API_KEY=/# GEMINI_API_KEY=/' .env

echo "✅ 已切换到 Ollama"
echo "请确保 Ollama 正在运行: ollama serve"
EOF

chmod +x switch_to_ollama.sh

# 创建切换到 Gemini 的脚本
cat > switch_to_gemini.sh << 'EOF'
#!/bin/bash
# 切换到 Gemini

# 备份当前 .env
cp .env .env.backup

# 更新配置
sed -i.bak 's/^LLM_PROVIDER=.*/LLM_PROVIDER=gemini/' .env

# 注释掉 Ollama
sed -i.bak 's/^OLLAMA_DEFAULT_MODEL=/# OLLAMA_DEFAULT_MODEL=/' .env

echo "✅ 已切换到 Gemini"
echo "请确保 GEMINI_API_KEY 已在 .env 中设置"
EOF

chmod +x switch_to_gemini.sh
```

## 验证当前使用的提供商

```bash
# 方法一：查看环境变量
grep LLM_PROVIDER .env

# 方法二：使用 Python 检查
uv run python -c "
import os
from dotenv import load_dotenv
load_dotenv()

provider = os.getenv('LLM_PROVIDER', 'gemini')
print(f'当前 LLM 提供商: {provider}')

if provider == 'ollama':
    print(f'模型: {os.getenv(\"OLLAMA_DEFAULT_MODEL\", \"dolphin3\")}')
    print(f'Base URL: {os.getenv(\"OLLAMA_BASE_URL\", \"http://localhost:11434\")}')
elif provider == 'gemini':
    api_key = os.getenv('GEMINI_API_KEY', '未设置')
    print(f'API Key: {\"已设置\" if api_key and api_key != \"未设置\" else \"未设置\"}')
"

# 方法三：通过代码检查
uv run python -c "
from src.llm.provider_factory import ProviderFactory
provider = ProviderFactory.create()
print(f'当前提供商: {provider.get_provider_name()}')
print(f'默认模型: {provider.get_default_model()}')
print(f'可用模型: {provider.get_available_models()[:3]}')
"
```

## 常见问题

### Q: 如何同时支持多个提供商？

A: 你可以在代码中为不同的代理指定不同的提供商：

```python
from src.coordination.coordinator import WorkflowCoordinator

# 为不同代理使用不同提供商
coordinator = WorkflowCoordinator()

# 或者在创建代理时指定
from src.agents.requirements_analyst import RequirementsAnalyst

# 使用 Ollama 的代理
ollama_agent = RequirementsAnalyst(provider_name="ollama")

# 使用 Gemini 的代理
gemini_agent = RequirementsAnalyst(provider_name="gemini")
```

### Q: 切换后需要重启服务吗？

A: 如果使用 Web 接口，需要重启：

```bash
# 停止当前服务（Ctrl+C）
# 然后重新启动
uv run python -m src.web.app
```

如果是命令行使用，重新运行命令即可。

### Q: 如何知道当前使用的是哪个提供商？

A: 查看日志输出，或运行：

```bash
uv run python -c "
from src.llm.provider_factory import ProviderFactory
provider = ProviderFactory.create()
print(f'Provider: {provider.get_provider_name()}')
"
```

### Q: Ollama 连接失败怎么办？

A: 检查以下几点：

1. **Ollama 是否运行**
   ```bash
   # 检查进程
   ps aux | grep ollama
   
   # 或测试连接
   curl http://localhost:11434/api/tags
   ```

2. **模型是否已下载**
   ```bash
   ollama list
   # 如果模型不存在，下载它
   ollama pull dolphin3
   ```

3. **端口是否正确**
   ```bash
   # 检查 .env 中的 OLLAMA_BASE_URL
   grep OLLAMA_BASE_URL .env
   ```

### Q: Gemini API 密钥无效怎么办？

A: 检查以下几点：

1. **API 密钥是否正确**
   - 访问 https://aistudio.google.com/app/apikey
   - 确认密钥已复制完整（没有多余空格）

2. **API 密钥是否有效**
   ```bash
   # 测试 API 密钥
   uv run python -c "
   from src.llm.provider_factory import ProviderFactory
   try:
       provider = ProviderFactory.create('gemini')
       print('✅ Gemini 连接成功')
   except Exception as e:
       print(f'❌ 错误: {e}')
   "
   ```

3. **环境变量是否加载**
   ```bash
   # 检查 .env 文件
   cat .env | grep GEMINI_API_KEY
   ```

## 推荐配置

### 开发环境（推荐 Ollama）

```env
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=dolphin3
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MAX_TOKENS=8192
ENVIRONMENT=dev
```

**原因：**
- 免费，无 API 成本
- 快速迭代，无速率限制
- 数据隐私

### 生产环境（推荐 Gemini）

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_production_api_key
ENVIRONMENT=prod
LOG_LEVEL=INFO
LOG_FORMAT=json
```

**原因：**
- 模型质量更高
- 更稳定可靠
- 自动维护和更新

## 总结

切换 LLM 提供商非常简单：

1. **编辑 .env 文件**，修改 `LLM_PROVIDER` 变量
2. **配置对应的参数**（API 密钥或 Ollama 设置）
3. **重启应用**（如果使用 Web 接口）
4. **验证切换**是否成功

**推荐：**
- 开发时使用 **Ollama**（免费、快速）
- 生产环境使用 **Gemini**（质量高、稳定）

