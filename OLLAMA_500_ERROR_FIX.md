# Ollama 500 服务器错误修复指南

## 问题描述

Ollama API 返回 500 Internal Server Error，这通常发生在：

1. **模型加载失败**：大型模型（如 mixtral 47B）需要大量内存
2. **内存不足**：Ollama 服务器内存耗尽
3. **模型文件损坏**：模型文件可能不完整或损坏
4. **服务器临时过载**：多个请求同时处理
5. **模型不存在**：请求的模型未安装或名称错误

## 错误示例

```
RuntimeError: Ollama API error: 500 Server Error: Internal Server Error for url: http://localhost:11434/api/chat
```

## 解决方案

### 1. 自动重试机制

系统现在会自动重试 500/503 错误：

- **重试次数**：最多 2 次
- **重试延迟**：2 秒（指数退避：2s → 3s）
- **适用错误**：500 (Internal Server Error), 503 (Service Unavailable)

### 2. 详细的错误信息

系统现在会提取并显示详细的错误信息：

```python
# 从响应中提取错误详情
error_details = error_response.get("error") or error_response.get("message")
```

### 3. 针对性的故障排除建议

根据 HTTP 状态码提供具体建议：

#### 404 - 模型未找到

```
Model 'mixtral' not found. 
Available models: dolphin3:latest, mixtral:latest. 
Try: ollama pull mixtral
```

#### 500 - 服务器内部错误

```
Ollama server internal error. Possible causes: 
1) Model 'mixtral' failed to load (check memory), 
2) Server out of memory, 3) Model file corruption. 
Try: ollama run mixtral (to test model), or use a smaller model like 'dolphin3'
```

#### 503 - 服务暂时不可用

```
Ollama server temporarily unavailable. 
Wait a few seconds and try again, or check if Ollama is running: ollama list
```

## 诊断步骤

### 1. 检查 Ollama 服务状态

```bash
# 检查 Ollama 是否运行
ollama list

# 检查可用模型
curl http://localhost:11434/api/tags
```

### 2. 测试模型

```bash
# 直接测试模型是否工作
ollama run mixtral "Hello, how are you?"

# 如果失败，查看错误信息
ollama run mixtral 2>&1 | head -20
```

### 3. 检查系统资源

```bash
# 检查内存使用
top -l 1 | grep -E "PhysMem|Memory"

# 检查 Ollama 进程
ps aux | grep ollama
```

### 4. 检查模型文件

```bash
# 查看模型信息
ollama show mixtral

# 重新拉取模型（如果损坏）
ollama pull mixtral
```

## 常见问题和解决方案

### 问题 1：内存不足

**症状**：
- 500 错误
- 模型加载失败
- 系统内存使用率高

**解决方案**：
1. 使用更小的模型：
   ```env
   OLLAMA_DEFAULT_MODEL=dolphin3  # 8B 模型，需要更少内存
   # OLLAMA_DEFAULT_MODEL=mixtral  # 47B 模型，需要更多内存
   ```

2. 关闭其他应用程序释放内存

3. 增加系统内存（如果可能）

4. 使用混合模式（关键文档用 Gemini）：
   ```env
   LLM_PROVIDER=ollama
   GEMINI_API_KEY=your_key
   # 关键文档自动使用 Gemini（不需要本地内存）
   ```

### 问题 2：模型加载失败

**症状**：
- 500 错误
- `ollama run mixtral` 失败

**解决方案**：
1. 重新拉取模型：
   ```bash
   ollama pull mixtral
   ```

2. 检查模型文件完整性：
   ```bash
   ollama show mixtral
   ```

3. 使用不同的模型版本：
   ```bash
   ollama pull mixtral:8x7b  # 使用较小的版本
   ```

### 问题 3：服务器临时过载

**症状**：
- 503 错误
- 间歇性 500 错误
- 多个请求同时处理

**解决方案**：
1. 等待几秒钟后重试（系统会自动重试）

2. 减少并发请求：
   ```python
   # 在 coordinator.py 中调整并发数
   max_workers = 2  # 减少并发数
   ```

3. 使用更快的模型（减少处理时间）：
   ```env
   OLLAMA_DEFAULT_MODEL=dolphin3  # 更快的模型
   ```

### 问题 4：模型名称错误

**症状**：
- 404 错误
- 模型未找到

**解决方案**：
1. 检查可用模型：
   ```bash
   ollama list
   ```

2. 使用正确的模型名称：
   ```env
   OLLAMA_DEFAULT_MODEL=dolphin3:latest  # 使用完整名称
   # 或
   OLLAMA_DEFAULT_MODEL=dolphin3  # 使用简短名称
   ```

3. 拉取缺失的模型：
   ```bash
   ollama pull dolphin3
   ```

## 配置建议

### 开发环境（快速迭代）

```env
OLLAMA_DEFAULT_MODEL=dolphin3    # 更快的模型，更少内存
OLLAMA_MAX_TOKENS=4096          # 减少 token 数
OLLAMA_TIMEOUT=300              # 5 分钟超时
```

### 生产环境（质量优先）

```env
OLLAMA_DEFAULT_MODEL=mixtral     # 更好的质量
OLLAMA_MAX_TOKENS=8192          # 更长的输出
OLLAMA_TIMEOUT=1800             # 30 分钟超时
```

### 混合模式（推荐）

```env
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=dolphin3    # 默认使用快速模型
OLLAMA_TIMEOUT=600
GEMINI_API_KEY=your_key

# 关键文档自动使用 Gemini（无内存限制，无 500 错误）
# 其他文档使用 Ollama
```

## 验证修复

### 检查错误处理

```python
from src.llm.ollama_provider import OllamaProvider

provider = OllamaProvider()

# 测试错误处理
try:
    result = provider.generate("Test prompt", model="nonexistent")
except RuntimeError as e:
    print(f"Error handled: {e}")
    # 应该显示详细的错误信息和建议
```

### 检查重试机制

查看日志中的重试信息：

```
WARNING | Ollama API server error (500): Internal server error. 
Retrying in 2.0s (attempt 1/3)...
WARNING | Ollama API server error (500): Internal server error. 
Retrying in 3.0s (attempt 2/3)...
```

## 最佳实践

1. **使用混合模式**：关键文档使用 Gemini，其他使用 Ollama
2. **监控内存使用**：确保有足够内存运行大型模型
3. **使用合适的模型**：根据任务选择模型大小
4. **检查 Ollama 状态**：定期检查 `ollama list` 和系统资源
5. **错误处理**：系统会自动重试，但也要监控日志

## 总结

已修复 Ollama 500 错误处理：

- ✅ **自动重试**：500/503 错误自动重试 2 次
- ✅ **详细错误信息**：提取并显示 Ollama 服务器错误详情
- ✅ **针对性建议**：根据错误类型提供具体解决方案
- ✅ **更好的日志**：记录重试次数和错误详情

**推荐配置**：
```env
OLLAMA_DEFAULT_MODEL=dolphin3    # 更稳定，更少内存问题
OLLAMA_TIMEOUT=600              # 10 分钟超时
# 或使用混合模式
GEMINI_API_KEY=your_key         # 关键文档使用 Gemini
```

如果仍然遇到 500 错误，建议：
1. 检查系统内存
2. 使用更小的模型（dolphin3）
3. 使用混合模式（关键文档用 Gemini）
4. 检查 Ollama 服务器日志

