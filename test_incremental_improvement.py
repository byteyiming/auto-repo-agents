#!/usr/bin/env python3
"""
测试增量迭代改进和逐个文档审批功能
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager
from src.context.shared_context import AgentType

async def test_incremental_improvement():
    """测试增量迭代改进功能"""
    print("=" * 80)
    print("🧪 测试增量迭代改进功能")
    print("=" * 80)
    print()
    
    context_manager = ContextManager()
    coordinator = WorkflowCoordinator(context_manager=context_manager)
    
    project_id = "test_incremental_improvement"
    user_idea = "创建一个简单的待办事项应用，支持任务创建、编辑、删除和标记完成"
    
    print(f"📝 项目ID: {project_id}")
    print(f"💡 用户想法: {user_idea}")
    print()
    
    try:
        # 测试 Phase 1 顺序执行和逐个文档审批
        print("🚀 开始生成 Phase 1 文档（顺序执行，逐个审批）...")
        print()
        
        # 注意：在实际运行中，这里会等待用户审批
        # 为了测试，我们可以设置一个较短的超时时间
        results = await coordinator.async_generate_all_docs(
            user_idea=user_idea,
            project_id=project_id,
            profile="individual",  # 使用 individual 以加快测试
            phase1_only=False  # 设置为 False 以测试完整流程
        )
        
        print()
        print("=" * 80)
        print("✅ 测试完成！")
        print("=" * 80)
        print()
        print("📄 生成的文档:")
        for doc_type, file_path in results.get('files', {}).items():
            status = results.get('status', {}).get(doc_type, 'unknown')
            print(f"  ✅ {doc_type}: {status}")
        
        # 检查文档版本
        print()
        print("📊 文档版本信息:")
        requirements_version = context_manager.get_document_version(project_id, AgentType.REQUIREMENTS_ANALYST)
        technical_version = context_manager.get_document_version(project_id, AgentType.TECHNICAL_DOCUMENTATION)
        print(f"  📄 Requirements: Version {requirements_version}")
        print(f"  📄 Technical Spec: Version {technical_version}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_incremental_improvement())

