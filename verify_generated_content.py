#!/usr/bin/env python3
"""
验证重新生成的文档内容是否正确
检查每个文档是否包含应有的特定内容
"""
import sys
from pathlib import Path

def verify_document_content(file_path: Path, doc_type: str) -> tuple[bool, str]:
    """验证单个文档内容"""
    if not file_path.exists():
        return False, "文件不存在"
    
    content = file_path.read_text(encoding='utf-8')
    
    # 检查是否包含requirements的重复内容（不应该有）
    if "## Project Overview" in content and "SmartJob Tracking" in content:
        # 检查是否只是requirements的重复
        if "## Core Features" in content and "Job Application Tracking:" in content:
            # 进一步检查是否真的只是requirements
            if "## Technical Requirements" in content and "Platform Compatibility:" in content:
                if "## User Personas" in content and "Recent Graduate (Sarah):" in content:
                    return False, "❌ 内容仍然是requirements的重复"
    
    # 根据文档类型检查特定内容
    if doc_type == "api":
        # API文档应该有端点
        has_endpoint = any(keyword in content for keyword in [
            "GET /", "POST /", "PUT /", "DELETE /",
            "/api/v1/", "/api/", "Endpoint", "endpoint",
            "Request", "Response", "status code"
        ])
        if not has_endpoint:
            return False, "❌ 缺少API端点信息"
        return True, "✅ 包含API端点"
    
    elif doc_type == "database":
        # 数据库文档应该有SQL语句
        has_sql = any(keyword in content for keyword in [
            "CREATE TABLE", "CREATE TABLE IF NOT EXISTS",
            "PRIMARY KEY", "FOREIGN KEY", "VARCHAR", "INT",
            "TIMESTAMP", "NOT NULL", "UNIQUE"
        ])
        if not has_sql:
            return False, "❌ 缺少SQL CREATE TABLE语句"
        return True, "✅ 包含SQL语句"
    
    elif doc_type == "user_stories":
        # 用户故事应该有特定格式
        has_story_format = any(keyword in content for keyword in [
            "As a ", "I want", "so that",
            "Given", "When", "Then",
            "Acceptance Criteria", "Story Points"
        ])
        if not has_story_format:
            return False, "❌ 缺少用户故事格式"
        return True, "✅ 包含用户故事格式"
    
    elif doc_type == "charter":
        # 项目章程应该有商业相关内容
        has_business = any(keyword in content for keyword in [
            "Executive Summary", "ROI", "Budget",
            "Business Case", "Stakeholder", "Timeline",
            "Risk", "Success Criteria"
        ])
        if not has_business:
            return False, "❌ 缺少商业案例内容"
        return True, "✅ 包含商业案例内容"
    
    elif doc_type == "technical":
        # 技术文档应该有技术栈和架构
        has_tech = any(keyword in content for keyword in [
            "Architecture", "Technology Stack", "Python",
            "FastAPI", "PostgreSQL", "React", "Docker",
            "System Design", "Components", "Database"
        ])
        if not has_tech:
            return False, "❌ 缺少技术架构内容"
        return True, "✅ 包含技术架构内容"
    
    elif doc_type == "setup":
        # 安装指南应该有命令
        has_commands = any(keyword in content for keyword in [
            "npm install", "pip install", "docker run",
            "git clone", "python -m", "uv run",
            "Installation", "Setup", "Prerequisites"
        ])
        if not has_commands:
            return False, "❌ 缺少安装命令"
        return True, "✅ 包含安装命令"
    
    return True, "✅ 文档存在"

def main():
    """主验证函数"""
    print("=" * 60)
    print("验证重新生成的文档内容")
    print("=" * 60)
    print()
    
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("❌ docs目录不存在")
        return False
    
    # 要检查的文档
    checks = [
        ("charter/project_charter.md", "charter"),
        ("api/api_documentation.md", "api"),
        ("database/database_schema.md", "database"),
        ("user_stories/user_stories.md", "user_stories"),
        ("technical/technical_spec.md", "technical"),
        ("setup/setup_guide.md", "setup"),
        ("pm/project_plan.md", "pm"),
    ]
    
    results = []
    for file_path, doc_type in checks:
        full_path = docs_dir / file_path
        is_valid, message = verify_document_content(full_path, doc_type)
        results.append((file_path, is_valid, message))
        
        status = "✅" if is_valid else "❌"
        print(f"{status} {file_path}: {message}")
    
    print()
    print("=" * 60)
    
    # 统计结果
    valid_count = sum(1 for _, is_valid, _ in results if is_valid)
    total_count = len(results)
    
    if valid_count == total_count:
        print(f"✅ 所有文档验证通过 ({valid_count}/{total_count})")
        print()
        print("文档内容正确！每个文档都包含了应有的特定内容。")
        return True
    else:
        print(f"⚠️  部分文档验证失败 ({valid_count}/{total_count} 通过)")
        print()
        print("失败的文档:")
        for file_path, is_valid, message in results:
            if not is_valid:
                print(f"  - {file_path}: {message}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

