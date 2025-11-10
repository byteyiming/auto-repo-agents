# Document Summary Length 配置指南

## 问题分析

从日志中可以看到，当前的 `max_summary_length=2000` 字符存在以下问题：

1. **部分摘要过短**：某些文档的摘要只有 796-921 字符，远低于目标
2. **部分摘要过长**：某些文档的摘要超过 2965-3073 字符，超过了目标
3. **不够灵活**：固定值无法适应不同大小和复杂度的文档

## 解决方案

### 1. 可配置的摘要长度

通过环境变量 `MAX_SUMMARY_LENGTH` 可以配置摘要的最大长度：

```env
# Document Summary Configuration
MAX_SUMMARY_LENGTH=3000      # Default: 3000 chars (increased from 2000)
```

### 2. 默认值调整

- **旧默认值**：2000 字符
- **新默认值**：3000 字符
- **原因**：增加默认值可以更好地覆盖复杂文档，同时仍然保持合理的长度

### 3. 动态调整建议

根据文档类型和大小，可以考虑以下配置：

| 文档类型 | 推荐长度 | 原因 |
|---------|---------|------|
| 需求文档 | 2000-3000 | 相对简单，不需要太多细节 |
| 技术文档 | 3000-4000 | 复杂，需要更多技术细节 |
| API 文档 | 3000-5000 | 包含大量端点和示例 |
| 数据库架构 | 2000-3000 | 结构化内容，相对简洁 |
| 测试文档 | 4000-5000 | 需要详细的测试用例和场景 |

## 配置方法

### 方法 1：环境变量（推荐）

在 `.env` 文件中设置：

```env
MAX_SUMMARY_LENGTH=3000
```

### 方法 2：代码中指定

```python
from src.utils.document_summarizer import DocumentSummarizer

# 使用自定义长度
summarizer = DocumentSummarizer(max_summary_length=4000)

# 或者使用环境变量（默认）
summarizer = DocumentSummarizer()
```

### 方法 3：在调用时覆盖

```python
from src.utils.document_summarizer import summarize_document

# 使用默认长度
summary = summarize_document(content, "technical_documentation")

# 使用自定义长度（通过 summarizer 实例）
summarizer = DocumentSummarizer()
summary = summarizer.summarize(content, "technical_documentation", max_length=5000)
```

## 最佳实践

1. **根据文档大小调整**：
   - 小文档 (< 5000 字符)：使用 2000-3000
   - 中等文档 (5000-20000 字符)：使用 3000-4000
   - 大文档 (> 20000 字符)：使用 4000-5000

2. **根据用途调整**：
   - **传递给其他代理**：使用较短的摘要 (2000-3000)
   - **用于质量检查**：使用较长的摘要 (3000-4000)
   - **用于用户查看**：使用完整文档或较长摘要 (4000+)

3. **监控摘要质量**：
   - 检查摘要是否包含关键信息
   - 确保摘要不会丢失重要细节
   - 验证摘要的逻辑完整性

## 验证配置

### 检查当前配置

```python
from src.utils.document_summarizer import DocumentSummarizer
import os

summarizer = DocumentSummarizer()
print(f"Max Summary Length: {summarizer.max_summary_length}")
print(f"Environment Variable: {os.getenv('MAX_SUMMARY_LENGTH', 'not set')}")
```

### 测试不同长度

```python
from src.utils.document_summarizer import DocumentSummarizer

content = "..."  # Your document content

# 测试不同长度
for length in [2000, 3000, 4000, 5000]:
    summarizer = DocumentSummarizer(max_summary_length=length)
    summary = summarizer.summarize(content, "technical_documentation")
    print(f"Length {length}: {len(summary)} chars")
    print(f"  Summary: {summary[:100]}...")
```

## 故障排除

### 问题 1：摘要过短，丢失关键信息

**解决方案**：
1. 增加 `MAX_SUMMARY_LENGTH` 到 4000 或 5000
2. 检查提示词是否要求保留关键信息
3. 验证 LLM 是否遵循指令

### 问题 2：摘要过长，超出目标

**说明**：这是正常的。LLM 可能生成略长于目标的摘要以确保完整性。

**解决方案**：
1. 如果摘要过长（> 150% 目标），检查提示词
2. 考虑使用更严格的长度限制
3. 或者接受稍长的摘要以获得更好的质量

### 问题 3：摘要质量不一致

**解决方案**：
1. 使用更低的 temperature（已在代码中设置为 0.3）
2. 改进提示词，明确要求
3. 增加 `MAX_SUMMARY_LENGTH` 给 LLM 更多空间

## 总结

- ✅ **默认值已提高**：从 2000 增加到 3000 字符
- ✅ **可配置**：通过 `MAX_SUMMARY_LENGTH` 环境变量
- ✅ **灵活**：可以在代码中动态调整
- ✅ **向后兼容**：现有代码无需修改

**推荐配置**：
```env
MAX_SUMMARY_LENGTH=3000
```

这个配置在摘要质量和长度之间取得了良好的平衡。

