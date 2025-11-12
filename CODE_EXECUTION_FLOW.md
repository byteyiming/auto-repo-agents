# 代码执行流程详解

## 🚀 总体流程概览

```
用户请求 → Web App → Coordinator → Agents → LLM → 文档生成 → 数据库 → 返回结果
```

---

## 📍 第一步：应用启动 (`src/web/app.py`)

### 1.1 服务器启动

```python
# 运行命令: uv run python -m src.web.app
# 入口点: src/web/app.py

# 1. FastAPI 应用初始化
app = FastAPI(title="DOCU-GEN API", version="1.0.0", lifespan=lifespan)
```

### 1.2 生命周期管理 (`lifespan`)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭时的处理"""
    # 启动时：
    global coordinator, context_manager
    context_manager = ContextManager()  # 创建 SQLite 数据库连接
    coordinator = WorkflowCoordinator(context_manager=context_manager)  # 创建协调器
    
    # 这里会初始化所有 21 个 Agent：
    # - RequirementsAnalyst
    # - TechnicalDocumentationAgent
    # - APIDocumentationAgent
    # - ... 等等
    # 每个 Agent 都会：
    #   1. 创建 LLM Provider (Gemini/Ollama/OpenAI，从 LLM_PROVIDER 环境变量读取)
    #   2. 配置 Phase 模型选择（根据当前 phase 自动选择模型）
    #   3. 创建 FileManager (文件管理器)
    #   4. 配置日志和速率限制
    
    yield  # 应用运行中...
    
    # 关闭时：清理资源（如果需要）
```

**关键点：**
- `ContextManager`: 管理 SQLite 数据库，存储项目状态和 Agent 输出
- `WorkflowCoordinator`: 协调所有 Agent 的工作流
- 所有 Agent 在启动时就被创建好，等待使用

---

## 📍 第二步：用户发起请求

### 2.1 前端发送请求

```javascript
// 前端 (index.html) 发送 POST 请求
fetch('/api/generate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        user_idea: "创建一个任务管理应用",
        profile: "team",
        workflow_mode: "docs_first"
    })
})
```

### 2.2 Web App 接收请求 (`/api/generate`)

```python
@app.post("/api/generate", response_model=GenerationResponse)
async def generate_docs(request: GenerationRequest):
    """接收文档生成请求"""
    
    # 1. 生成项目 ID
    project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # 2. 在数据库中创建项目记录
    context_manager.create_project(project_id, request.user_idea)
    context_manager.update_project_status(
        project_id=project_id,
        status="in_progress",  # 状态：进行中
        user_idea=request.user_idea,
        profile=request.profile,
        completed_agents=[]  # 还没有完成的 Agent
    )
    
    # 3. 异步启动文档生成（不阻塞 HTTP 响应）
    asyncio.create_task(
        run_generation_async(
            request.user_idea,
            project_id,
            request.profile,
            request.provider_name,
            request.codebase_path,
            request.workflow_mode
        )
    )
    
    # 4. 立即返回响应（不等待生成完成）
    return GenerationResponse(
        project_id=project_id,
        status="started",
        message="Documentation generation started"
    )
```

**关键点：**
- 使用 `asyncio.create_task` 在后台运行，不阻塞 HTTP 响应
- 立即返回项目 ID，前端可以用它来查询状态
- 状态存储在 SQLite 数据库中

---

## 📍 第三步：异步生成文档 (`run_generation_async`)

### 3.1 初始化生成任务

```python
async def run_generation_async(
    user_idea: str,
    project_id: str,
    profile: str = "team",
    provider_name: Optional[str] = None,
    codebase_path: Optional[str] = None,
    workflow_mode: str = "docs_first"
):
    """异步生成文档"""
    
    # 1. 发送 WebSocket 进度更新
    await websocket_manager.send_progress(project_id, {
        "type": "start",
        "message": "Documentation generation started"
    })
    
    # 2. 获取或创建 Coordinator
    if provider_name:
        local_coordinator = WorkflowCoordinator(
            context_manager=context_manager,
            provider_name=provider_name
        )
    else:
        local_coordinator = coordinator  # 使用全局 coordinator
    
    # 3. 调用 Coordinator 的异步生成方法
    results = await local_coordinator.async_generate_all_docs(
        user_idea=user_idea,
        project_id=project_id,
        profile=profile,
        codebase_path=codebase_path,
        workflow_mode=workflow_mode
    )
    
    # 4. 更新数据库状态
    context_manager.update_project_status(
        project_id=project_id,
        status="complete",
        completed_agents=list(results.get("files", {}).keys()),
        results=results
    )
```

**关键点：**
- 使用 WebSocket 实时推送进度
- 调用 `WorkflowCoordinator.async_generate_all_docs` 执行实际工作
- 完成后更新数据库状态

---

## 📍 第四步：WorkflowCoordinator 执行工作流

### 4.1 工作流初始化 (`async_generate_all_docs`)

```python
async def async_generate_all_docs(
    self,
    user_idea: str,
    project_id: str,
    profile: str = "team",
    codebase_path: Optional[str] = None,
    workflow_mode: str = "docs_first"
) -> Dict:
    """生成所有文档类型（异步版本）"""
    
    # 1. 初始化结果字典
    results = {
        "project_id": project_id,
        "user_idea": user_idea,
        "profile": profile,
        "workflow_mode": workflow_mode,
        "files": {},  # 存储生成的文件路径
        "status": {}  # 存储每个文档的状态
    }
    
    # 2. 存储最终文档内容
    final_docs = {}  # AgentType -> content
    document_file_paths = {}  # AgentType -> file_path
```

### 4.2 Phase 0: 代码分析（Code-First 模式）

```python
# 如果是 code-first 模式，先分析代码
if workflow_mode == "code_first" and codebase_path:
    # 1. 分析代码库结构
    code_analysis_result = await loop.run_in_executor(
        None,
        lambda: self.code_analyst.analyze_codebase(codebase_path)
    )
    # 结果包含：modules, classes, functions, docstrings 等
    
    # 2. 生成代码分析摘要
    code_analysis_summary = "..."
    # 这个摘要会在 Phase 1 和 Phase 2 中传递给相关 Agent
```

---

## 📍 第五步：Phase 1 - 基础文档生成（DAG + 质量门控）

### 5.1 获取 Phase 1 任务配置

```python
# 从 workflow_dag.py 获取任务配置
phase1_tasks = get_phase1_tasks_for_profile(profile=profile)
# 返回：
# [
#     Phase1Task(
#         task_id="requirements",
#         agent_type=AgentType.REQUIREMENTS_ANALYST,
#         dependencies=[],  # 没有依赖
#         quality_threshold=80.0
#     ),
#     Phase1Task(
#         task_id="project_charter",
#         agent_type=AgentType.PROJECT_CHARTER,
#         dependencies=["requirements"],  # 依赖 requirements
#         quality_threshold=75.0
#     ),
#     ...
# ]
```

### 5.2 构建依赖关系图

```python
# 构建依赖关系映射
phase1_dependency_map = build_phase1_task_dependencies(phase1_tasks)
# 返回：
# {
#     "requirements": [],  # 没有依赖
#     "project_charter": ["requirements"],
#     "user_stories": ["requirements", "project_charter"],
#     "technical_doc": ["requirements", "user_stories"],
#     "database_schema": ["requirements", "technical_doc"]
# }
```

### 5.3 创建异步执行器

```python
# 创建异步并行执行器
executor = AsyncParallelExecutor(max_workers=4)

# 为每个任务创建异步协程
for task in phase1_tasks:
    task_coro = create_phase1_task_coro(task)()
    executor.add_task(
        task_id=task.task_id,
        coro=task_coro,
        dependencies=phase1_dependency_map[task.task_id]
    )

# 执行任务（自动处理依赖关系）
phase1_task_results = await executor.execute()
```

### 5.4 执行单个 Phase 1 任务（带质量门控）

```python
async def execute_phase1_task():
    """执行 Phase 1 任务"""
    
    # 1. 获取依赖任务的输出
    deps_content = {}
    for dep_type in task.dependencies:
        dep_output = await context_manager.get_agent_output(project_id, dep_type)
        deps_content[dep_type] = dep_output.content
    
    # 2. 构建 Agent 的参数
    kwargs = build_kwargs_for_phase1_task(
        task=task,
        user_idea=user_idea,
        project_id=project_id,
        context_manager=context_manager,
        deps_content=deps_content,
        code_analysis_summary=code_analysis_summary
    )
    
    # 3. 获取 Agent 实例
    agent = get_agent_for_phase1_task(self, task.agent_type)
    # 例如：RequirementsAnalyst, TechnicalDocumentationAgent 等
    
    # 4. 执行质量门控循环
    file_path, content = await self._async_run_agent_with_quality_loop(
        agent_instance=agent,
        agent_type=task.agent_type,
        generate_kwargs=kwargs,
        quality_threshold=task.quality_threshold  # 例如：80.0
    )
    
    return file_path, content
```

### 5.5 质量门控循环 (`_async_run_agent_with_quality_loop`)

```python
async def _async_run_agent_with_quality_loop(
    self,
    agent_instance,
    agent_type: AgentType,
    generate_kwargs: Dict,
    quality_threshold: float = 70.0
):
    """质量门控循环：生成 → 检查 → 改进 → 再检查"""
    
    max_iterations = 3
    for iteration in range(1, max_iterations + 1):
        # 1. 生成文档 V1
        logger.info(f"  📝 Step {iteration}: Generating V{iteration}...")
        content_v1 = await agent_instance.async_generate(**generate_kwargs)
        
        # 2. 质量检查
        logger.info(f"  🔍 Step {iteration}: Checking quality...")
        quality_result = await self.quality_checker.check_quality(
            content=content_v1,
            agent_type=agent_type
        )
        # 返回：{
        #     "score": 85.0,
        #     "word_count": 1200,
        #     "sections_complete": True,
        #     "readability": 65.0,
        #     "missing_sections": [],
        #     "details": {...}
        # }
        
        # 3. 检查是否达到阈值
        if quality_result["score"] >= quality_threshold:
            logger.info(f"  ✅ Quality threshold met: {quality_result['score']:.1f} >= {quality_threshold}")
            # 保存到数据库
            await self._save_agent_output_async(agent_type, content_v1, project_id)
            return file_path, content_v1
        
        # 4. 如果未达标，改进文档
        if iteration < max_iterations:
            logger.info(f"  🔧 Step {iteration}: Improving document...")
            improved_content = await self.document_improver.improve_document(
                original_content=content_v1,
                agent_type=agent_type,
                quality_score=quality_result["score"],
                quality_details=quality_result["details"]
            )
            content_v1 = improved_content
    
    # 如果 3 次迭代后仍未达标，返回最后一次的结果
    return file_path, content_v1
```

**关键点：**
- 使用 DAG 管理任务依赖关系
- 自动并行执行无依赖的任务
- 每个任务都有质量门控（生成 → 检查 → 改进）
- 最多迭代 3 次，直到达到质量阈值

---

## 📍 第六步：Phase 2 - 并行生成次级文档

### 6.1 获取 Phase 2 任务配置

```python
# 从 workflow_dag.py 获取 Phase 2 任务
phase2_tasks = get_phase2_tasks_for_profile(profile=profile)
# 返回：
# [
#     Phase2Task(
#         task_id="api_documentation",
#         agent_type=AgentType.API_DOCUMENTATION,
#         dependencies=[AgentType.TECHNICAL_DOCUMENTATION, AgentType.DATABASE_SCHEMA]
#     ),
#     Phase2Task(
#         task_id="setup_guide",
#         agent_type=AgentType.SETUP_GUIDE,
#         dependencies=[AgentType.API_DOCUMENTATION, AgentType.TECHNICAL_DOCUMENTATION]
#     ),
#     ...
# ]
```

### 6.2 执行 Phase 2 任务

```python
# 创建异步执行器
executor = AsyncParallelExecutor(max_workers=8)

# 为每个任务创建异步协程
for task in phase2_tasks:
    task_coro = create_async_task_coro(task)()
    executor.add_task(
        task_id=task.task_id,
        coro=task_coro,
        dependencies=dependency_map[task.task_id]
    )

# 并行执行（自动处理依赖）
parallel_results = await executor.execute()
```

### 6.3 执行单个 Phase 2 任务

```python
async def execute_async_task():
    """执行 Phase 2 任务"""
    
    # 1. 获取依赖内容
    deps_content = {
        AgentType.REQUIREMENTS_ANALYST: req_content,
        AgentType.TECHNICAL_DOCUMENTATION: technical_summary,
        AgentType.DATABASE_SCHEMA: database_schema_summary,
        ...
    }
    
    # 2. 构建 Agent 参数
    kwargs = build_kwargs_for_task(
        task=task,
        coordinator=self,
        req_summary=req_summary,
        technical_summary=technical_summary,
        deps_content=deps_content,
        code_analysis_summary=code_analysis_summary
    )
    
    # 3. 获取 Agent 实例
    agent = get_agent_for_task(self, task.agent_type)
    
    # 4. 调用 Agent 生成文档
    if hasattr(agent, 'async_generate_and_save'):
        result = await agent.async_generate_and_save(**kwargs)
    else:
        # 同步版本在 executor 中运行
        result = await loop.run_in_executor(
            None,
            lambda: agent.generate_and_save(**kwargs)
        )
    
    return result  # 返回文件路径
```

**关键点：**
- Phase 2 任务没有质量门控（因为它们依赖 Phase 1 的高质量文档）
- 使用更大的线程池（8 个 worker）并行执行
- 自动处理任务依赖关系

---

## 📍 第七步：Agent 生成文档

### 7.1 Agent 调用 LLM

```python
# 例如：RequirementsAnalyst.generate()
class RequirementsAnalyst(BaseAgent):
    def generate(self, user_idea: str, **kwargs) -> str:
        """生成需求文档"""
        
        # 1. 构建 Prompt
        prompt = get_requirements_prompt(user_idea)
        
        # 2. 调用 LLM
        response = self.llm_provider.generate(
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        # LLM Provider 可能是：
        # - GeminiProvider (调用 Google Gemini API)
        # - OllamaProvider (调用本地 Ollama)
        # - OpenAIProvider (调用 OpenAI API)
        # 
        # 模型选择：
        # - 如果配置了 Phase 模型（如 OLLAMA_PHASE1_MODEL），会自动使用对应 phase 的模型
        # - 否则使用默认模型（如 OLLAMA_DEFAULT_MODEL）
        # - 支持为不同 phase 配置不同模型，实现速度和质量的平衡
        
        # 3. 清理响应
        cleaned_response = self._clean_response(response)
        
        # 4. 解析结构化数据（如果需要）
        parsed_data = self._parse_requirements(cleaned_response)
        
        return cleaned_response
```

### 7.2 LLM Provider 调用 API

```python
# 例如：GeminiProvider.generate()
class GeminiProvider(BaseLLMProvider):
    def generate(self, prompt: str, **kwargs) -> str:
        """调用 Gemini API"""
        
        # 1. 速率限制检查
        self.rate_limiter.wait_if_needed()
        
        # 2. 调用 Gemini API
        response = self.client.generate_content(
            model=self.model_name,
            contents=prompt,
            generation_config={
                "temperature": kwargs.get("temperature", 0.7),
                "max_output_tokens": kwargs.get("max_tokens", 8192)
            }
        )
        
        # 3. 提取文本
        text = response.text
        
        # 4. 缓存响应（可选）
        self.cache.set(prompt_hash, text)
        
        return text
```

### 7.3 保存文档到文件

```python
# Agent.generate_and_save()
def generate_and_save(self, output_filename: str, **kwargs) -> str:
    """生成并保存文档"""
    
    # 1. 生成文档内容
    content = self.generate(**kwargs)
    
    # 2. 保存到文件
    file_path = self.file_manager.write_file(
        filename=output_filename,
        content=content
    )
    # FileManager 会：
    # - 创建目录（如果不存在）
    # - 写入文件
    # - 返回完整路径
    
    # 3. 保存到数据库（通过 context_manager）
    self.context_manager.save_agent_output(
        project_id=project_id,
        agent_type=self.agent_type,
        content=content,
        file_path=file_path
    )
    
    return file_path
```

**关键点：**
- Agent 负责生成文档内容
- LLM Provider 负责调用 LLM API
- FileManager 负责文件操作
- ContextManager 负责数据库存储

---

## 📍 第八步：Phase 3 - 最终包装

### 8.1 交叉引用

```python
# 在所有文档中添加交叉引用链接
referenced_docs = self.cross_referencer.create_cross_references(
    final_docs,  # 所有文档内容
    document_file_paths  # 所有文档路径
)
# 例如：在 API 文档中引用 Technical 文档
# "详情请参考 [Technical Documentation](./technical/technical_spec.md)"
```

### 8.2 质量审查

```python
# 生成质量审查报告
quality_review_path = self.quality_reviewer.generate_and_save(
    all_documentation=all_documentation_for_review,
    output_filename="quality_review.md",
    project_id=project_id,
    context_manager=context_manager
)
```

### 8.3 格式转换

```python
# 转换文档格式（HTML, PDF, DOCX）
format_results = self.format_converter.convert_all_documents(
    documents=documents_for_conversion,
    formats=["html", "pdf", "docx"],
    project_id=project_id,
    context_manager=context_manager
)
# 返回：
# {
#     "requirements.md": {
#         "html": {"status": "success", "file_path": "..."},
#         "pdf": {"status": "failed_dependency_error", "error": "..."},
#         "docx": {"status": "success", "file_path": "..."}
#     },
#     ...
# }
```

---

## 📍 第九步：Phase 4 - 代码分析（Docs-First 模式）

```python
# 如果是 docs-first 模式，在文档生成后分析代码
if workflow_mode == "docs_first" and codebase_path:
    # 1. 分析代码库
    code_analysis = await self.code_analyst.analyze_codebase(codebase_path)
    
    # 2. 更新 API 文档
    updated_api_doc = await self.code_analyst.generate_code_documentation(
        code_analysis=code_analysis,
        existing_docs=api_doc_content
    )
    
    # 3. 更新开发者文档
    updated_dev_doc = await self.code_analyst.generate_code_documentation(
        code_analysis=code_analysis,
        existing_docs=dev_doc_content
    )
```

---

## 📍 第十步：返回结果

### 10.1 构建结果字典

```python
results = {
    "project_id": project_id,
    "user_idea": user_idea,
    "profile": profile,
    "workflow_mode": workflow_mode,
    "files": {
        "requirements": "docs/requirements/requirements.md",
        "technical_documentation": "docs/technical/technical_spec.md",
        "api_documentation": "docs/api/api_documentation.md",
        ...
    },
    "status": {
        "requirements": "complete_v2",
        "technical_documentation": "complete_v2",
        "api_documentation": "complete",
        ...
    },
    "execution_summary": {
        "total_documents": 21,
        "successful_count": 20,
        "failed_count": 1,
        "success_rate": 95.2
    },
    "documents_by_level": {
        "level_1_strategic": {...},
        "level_2_product": {...},
        "level_3_technical": {...},
        "cross_level": {...}
    }
}
```

### 10.2 更新数据库状态

```python
# 在 run_generation_async 中
context_manager.update_project_status(
    project_id=project_id,
    status="complete",
    completed_agents=list(results.get("files", {}).keys()),
    results=results
)
```

### 10.3 发送 WebSocket 更新

```python
# 发送完成消息
await websocket_manager.send_progress(project_id, {
    "type": "complete",
    "message": "Documentation generation complete",
    "project_id": project_id,
    "files_count": len(results.get('files', {}))
})
```

---

## 📍 第十一步：前端获取结果

### 11.1 查询状态

```javascript
// 前端轮询或通过 WebSocket 接收更新
const response = await fetch(`/api/status/${projectId}`);
const data = await response.json();
// {
//     "project_id": "...",
//     "status": "complete",
//     "completed_agents": ["requirements", "technical_documentation", ...],
//     "error": null
// }
```

### 11.2 获取结果

```javascript
// 获取所有生成的文档
const response = await fetch(`/api/results/${projectId}`);
const data = await response.json();
// {
//     "files": {...},
//     "documents_by_level": {...},
//     "summary": {...}
// }
```

### 11.3 下载文档

```javascript
// 下载单个文档
window.open(`/api/download/${projectId}/${docType}`);

// 或下载所有文档（ZIP）
window.open(`/api/download-all/${projectId}`);
```

---

## 🔄 完整流程图

```
1. 用户访问 http://localhost:8000
   ↓
2. FastAPI 启动，初始化 Coordinator 和所有 Agent
   ↓
3. 用户提交项目想法
   ↓
4. POST /api/generate
   ↓
5. 创建项目记录（数据库）
   ↓
6. asyncio.create_task(run_generation_async(...))
   ↓
7. WorkflowCoordinator.async_generate_all_docs()
   ↓
8. Phase 0: 代码分析（如果 code-first）
   ↓
9. Phase 1: 基础文档（DAG + 质量门控）
   ├─ RequirementsAnalyst → 生成需求文档
   ├─ ProjectCharterAgent → 生成项目章程
   ├─ UserStoriesAgent → 生成用户故事
   ├─ TechnicalDocumentationAgent → 生成技术文档
   └─ DatabaseSchemaAgent → 生成数据库设计
   ↓
10. Phase 2: 次级文档（并行执行）
    ├─ APIDocumentationAgent → 生成 API 文档
    ├─ SetupGuideAgent → 生成安装指南
    ├─ DeveloperDocumentationAgent → 生成开发者文档
    ├─ TestDocumentationAgent → 生成测试文档
    └─ ... (更多文档)
    ↓
11. Phase 3: 最终包装
    ├─ CrossReferencer → 添加交叉引用
    ├─ QualityReviewerAgent → 生成质量报告
    └─ FormatConverterAgent → 转换格式（HTML/PDF/DOCX）
    ↓
12. Phase 4: 代码分析（如果 docs-first）
    └─ CodeAnalystAgent → 分析代码并更新文档
    ↓
13. 更新数据库状态为 "complete"
    ↓
14. 发送 WebSocket 完成消息
    ↓
15. 前端显示结果，用户可以下载文档
```

---

## 🎯 关键组件说明

### 1. **ContextManager** (SQLite 数据库)
- 存储项目状态
- 存储每个 Agent 的输出
- 存储共享上下文（requirements, technical_summary 等）

### 2. **WorkflowCoordinator** (工作流协调器)
- 管理整个工作流
- 协调所有 Agent 的执行
- 处理任务依赖关系
- 管理质量门控循环

### 3. **AsyncParallelExecutor** (异步并行执行器)
- 并行执行多个任务
- 自动处理依赖关系（DAG）
- 支持异步操作

### 4. **Agent** (文档生成代理)
- 每个 Agent 负责生成一种类型的文档
- 使用 LLM Provider 调用 LLM API
- 使用 FileManager 保存文件
- 使用 ContextManager 存储结果

### 5. **LLM Provider** (LLM 提供商)
- GeminiProvider: 调用 Google Gemini API
- OllamaProvider: 调用本地 Ollama
- OpenAIProvider: 调用 OpenAI API

### 6. **QualityChecker** (质量检查器)
- 检查文档质量（字数、章节完整性、可读性等）
- 返回质量分数和改进建议

### 7. **DocumentImprover** (文档改进器)
- 根据质量检查结果改进文档
- 使用 LLM 重新生成改进版本

---

## 📊 数据流

```
用户输入 (user_idea)
    ↓
RequirementsAnalyst → requirements.md + 结构化数据
    ↓
ProjectCharterAgent → project_charter.md (依赖 requirements)
    ↓
UserStoriesAgent → user_stories.md (依赖 requirements + project_charter)
    ↓
TechnicalDocumentationAgent → technical_spec.md (依赖 requirements + user_stories)
    ↓
DatabaseSchemaAgent → database_schema.md (依赖 requirements + technical_doc)
    ↓
APIDocumentationAgent → api_documentation.md (依赖 technical_doc + database_schema)
    ↓
... (更多文档)
    ↓
CrossReferencer → 添加交叉引用
    ↓
QualityReviewerAgent → quality_review.md
    ↓
FormatConverterAgent → HTML/PDF/DOCX
    ↓
最终结果 (results dictionary)
```

---

## 🔍 调试技巧

1. **查看日志**：所有关键步骤都有日志输出
2. **检查数据库**：查看 `context.db` 中的项目状态
3. **查看文件**：检查 `docs/` 目录中生成的文件
4. **WebSocket 消息**：查看浏览器控制台中的 WebSocket 消息
5. **API 端点**：使用 `/api/status/{project_id}` 查询状态

---

## 💡 性能优化

1. **并行执行**：Phase 1 和 Phase 2 使用 DAG 并行执行
2. **异步操作**：使用 async/await 避免阻塞
3. **速率限制**：使用 RequestQueue 控制 API 调用频率
4. **缓存**：LLM 响应可以被缓存（如果启用）
5. **质量门控**：只在 Phase 1 使用，Phase 2 依赖 Phase 1 的高质量输出

---

这就是整个代码的执行流程！从用户请求开始，到最终生成文档并返回结果。

