# Temperature 配置指南

## 什么是 Temperature？

**Temperature（温度）** 参数控制 LLM 输出的"随机性"或"创造性"：

- **高 Temperature (0.8 - 1.0)**：模型更有创造性，更"敢说"，但更容易偏离指令、产生幻觉或"漂移"
- **低 Temperature (0.1 - 0.5)**：模型更"专注"、更"确定"，会严格遵循提示词，输出更可预测

## 为什么需要配置 Temperature？

对于 OmniDoc 项目，我们的目标是**生成高度结构化、严格遵循指令的专业文档**（例如，必须包含 `## System Architecture` 这样的标题）。

**本地模型（如 Ollama）需要更低的 Temperature** 来：
- 严格遵循复杂的指令
- 减少"漂移"和"遗忘"约束
- 提高输出的可预测性和一致性
- 确保文档结构的完整性

**云端模型（如 Gemini）可以使用稍高的 Temperature**，因为它们：
- 具有更强的指令遵循能力
- 可以处理更复杂的提示词
- 在保持准确性的同时允许一定的创造性

## 环境变量配置

### 基本配置

在 `.env` 文件中添加以下配置：

```env
# Temperature Configuration
# Default temperature for all providers (if not specified)
TEMPERATURE=0.3

# Provider-specific temperature overrides
OLLAMA_TEMPERATURE=0.3      # Lower for local models (better instruction following)
GEMINI_TEMPERATURE=0.7      # Higher for cloud models (balanced)
OPENAI_TEMPERATURE=0.7      # Higher for cloud models (balanced)
```

### 配置说明

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `TEMPERATURE` | `0.3` | 所有提供商的默认温度（如果未指定提供商特定值） |
| `OLLAMA_TEMPERATURE` | `0.3` | Ollama 本地模型的温度（推荐：0.2-0.4） |
| `GEMINI_TEMPERATURE` | `0.7` | Gemini 云端模型的温度（推荐：0.5-0.8） |
| `OPENAI_TEMPERATURE` | `0.7` | OpenAI 云端模型的温度（推荐：0.5-0.8） |

### 推荐值

#### 开发环境（Ollama）

```env
# 使用本地模型，需要严格遵循指令
TEMPERATURE=0.3
OLLAMA_TEMPERATURE=0.3
```

#### 生产环境（混合模式）

```env
# 本地模型使用低温度，云端模型使用中等温度
TEMPERATURE=0.3
OLLAMA_TEMPERATURE=0.3      # 本地模型：严格遵循指令
GEMINI_TEMPERATURE=0.7      # 云端模型：平衡质量和创造性
```

#### 高质量模式（全部 Gemini）

```env
# 全部使用云端模型，可以使用稍高的温度
TEMPERATURE=0.7
GEMINI_TEMPERATURE=0.7
```

## 代码中的使用

### 自动配置

Temperature 配置会自动从环境变量读取，并根据提供商应用到相应的代理：

```python
from src.agents.requirements_analyst import RequirementsAnalyst

# 自动使用环境变量中的温度配置
agent = RequirementsAnalyst(provider_name="ollama")
# Ollama 代理会自动使用 OLLAMA_TEMPERATURE (默认 0.3)

agent = RequirementsAnalyst(provider_name="gemini")
# Gemini 代理会自动使用 GEMINI_TEMPERATURE (默认 0.7)
```

### 手动覆盖

如果需要为特定调用覆盖温度：

```python
# 使用默认温度（从环境变量读取）
result = agent._call_llm(prompt)

# 手动指定温度
result = agent._call_llm(prompt, temperature=0.5)
```

### 特殊代理的温度设置

某些代理已经设置了特定的温度值（用于特殊用途）：

- **Legal Compliance Agent**: `temperature=0.5`（法律准确性）
- **Document Improver Agent**: `temperature=0.5`（一致性改进）
- **Document Summarizer**: `temperature=0.3`（一致性摘要）

这些代理会继续使用它们特定的温度值，不会被环境变量覆盖。

## 温度值选择指南

### 对于本地模型（Ollama）

| 温度值 | 效果 | 适用场景 |
|--------|------|----------|
| 0.1 - 0.3 | 非常严格，高度可预测 | **推荐**：技术文档、API 文档、数据库架构 |
| 0.3 - 0.5 | 平衡严格性和创造性 | 用户文档、测试文档 |
| 0.5 - 0.7 | 更有创造性 | 不推荐用于结构化文档 |
| 0.7+ | 高随机性，容易漂移 | 不推荐 |

### 对于云端模型（Gemini/OpenAI）

| 温度值 | 效果 | 适用场景 |
|--------|------|----------|
| 0.3 - 0.5 | 严格遵循指令 | 技术文档、API 文档 |
| 0.5 - 0.7 | **推荐**：平衡质量和创造性 | 大多数文档类型 |
| 0.7 - 0.9 | 更有创造性 | 创意内容、营销文档 |
| 0.9+ | 高随机性 | 不推荐用于文档生成 |

## 验证配置

### 检查当前温度设置

```python
from src.agents.requirements_analyst import RequirementsAnalyst
from src.config.settings import get_settings

# 检查设置
settings = get_settings()
print(f"Ollama Temperature: {settings.ollama_temperature}")
print(f"Gemini Temperature: {settings.gemini_temperature}")
print(f"OpenAI Temperature: {settings.openai_temperature}")

# 检查代理使用的温度
agent = RequirementsAnalyst(provider_name="ollama")
print(f"Agent Temperature: {agent.default_temperature}")
```

### 查看日志

代理初始化时会记录使用的温度：

```
INFO: RequirementsAnalyst initialized with provider: ollama, model: dolphin3, temperature: 0.3
```

LLM 调用时也会记录温度：

```
DEBUG: RequirementsAnalyst calling LLM (model: dolphin3, prompt length: 1234, temperature: 0.3)
```

## 故障排除

### 问题 1：文档质量不佳，结构不完整

**可能原因**：温度设置过高

**解决方案**：
1. 降低 `OLLAMA_TEMPERATURE` 到 `0.2` 或 `0.3`
2. 重新生成文档
3. 检查日志确认温度已更新

### 问题 2：文档过于呆板，缺乏细节

**可能原因**：温度设置过低

**解决方案**：
1. 适当提高温度到 `0.4` 或 `0.5`
2. 重新生成文档
3. 在质量和创造性之间找到平衡

### 问题 3：不同代理使用不同的温度

**说明**：这是正常的。某些代理（如 Legal Compliance）有特定的温度设置。

**验证**：
```python
from src.agents.legal_compliance_agent import LegalComplianceAgent

agent = LegalComplianceAgent()
# 查看代理的默认温度
print(f"Legal Agent Temperature: {agent.default_temperature}")
# 但在调用时可能会使用 0.5（硬编码）
```

## 最佳实践

1. **开发环境**：使用低温度（0.3）确保严格遵循指令
2. **生产环境**：
   - 本地模型：0.3（严格）
   - 云端模型：0.7（平衡）
3. **测试不同值**：根据项目需求调整温度
4. **监控日志**：查看实际使用的温度值
5. **文档质量检查**：使用 Quality Reviewer 检查温度对质量的影响

## 总结

Temperature 配置是提高本地模型（Ollama）生成文档质量的关键：

- ✅ **默认值已优化**：Ollama 0.3，Gemini 0.7
- ✅ **自动配置**：根据提供商自动选择温度
- ✅ **可自定义**：通过环境变量轻松调整
- ✅ **向后兼容**：现有代码无需修改

**推荐配置**：
```env
TEMPERATURE=0.3
OLLAMA_TEMPERATURE=0.3
GEMINI_TEMPERATURE=0.7
OPENAI_TEMPERATURE=0.7
```

这个配置在质量、一致性和成本之间取得了最佳平衡。

