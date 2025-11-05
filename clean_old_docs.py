#!/usr/bin/env python3
"""
清理旧文档和数据库记录
确保重新生成时使用新的prompts
"""
import sys
from pathlib import Path
import sqlite3

def clean_database():
    """清理数据库中的旧agent输出"""
    db_path = Path("context.db")
    if not db_path.exists():
        print("✅ context.db 不存在，无需清理")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有项目ID
        cursor.execute("SELECT DISTINCT project_id FROM agent_outputs")
        projects = cursor.fetchall()
        
        if not projects:
            print("✅ 数据库中没有agent输出记录")
            conn.close()
            return
        
        print(f"找到 {len(projects)} 个项目")
        
        # 删除所有agent输出（保留requirements表）
        cursor.execute("DELETE FROM agent_outputs")
        deleted = cursor.rowcount
        conn.commit()
        
        print(f"✅ 已删除 {deleted} 条agent输出记录")
        print("✅ 保留了requirements记录（用于参考）")
        
        conn.close()
    except Exception as e:
        print(f"⚠️  清理数据库时出错: {e}")

def verify_cleanup():
    """验证清理结果"""
    docs_dir = Path("docs")
    
    # 检查应该保留的文件
    keep_files = ["requirements.md", "index.md"]
    for keep_file in keep_files:
        if (docs_dir / keep_file).exists():
            print(f"✅ 保留: {keep_file}")
        elif keep_file == "index.md":
            print(f"ℹ️  {keep_file} 不存在（正常，会在生成时创建）")
    
    # 检查应该被删除的文档类型
    doc_types = [
        "charter/project_charter.md",
        "api/api_documentation.md",
        "database/database_schema.md",
        "user_stories/user_stories.md",
        "setup/setup_guide.md",
        "pm/project_plan.md",
        "technical/technical_spec.md",
    ]
    
    found = []
    for doc_type in doc_types:
        if (docs_dir / doc_type).exists():
            found.append(doc_type)
    
    if found:
        print(f"⚠️  以下文件仍然存在: {found}")
        return False
    else:
        print("✅ 所有旧文档已清理")
        return True

if __name__ == "__main__":
    print("=" * 60)
    print("清理旧文档和数据库")
    print("=" * 60)
    print()
    
    print("1. 清理数据库...")
    clean_database()
    print()
    
    print("2. 验证清理结果...")
    if verify_cleanup():
        print()
        print("=" * 60)
        print("✅ 清理完成！现在可以重新生成文档了")
        print("=" * 60)
        print()
        print("下一步:")
        print("1. 通过Web界面 (http://localhost:8000) 重新生成文档")
        print("2. 或使用API: POST /api/generate")
        print()
        print("重新生成后，每个文档应该包含正确的内容:")
        print("- API文档: 实际REST端点")
        print("- 数据库文档: SQL CREATE TABLE语句")
        print("- 用户故事: 'As a... I want... So that...'格式")
        print("- 项目章程: Executive Summary, ROI, Budget")
        print("- 技术规格: 具体技术栈选择")
    else:
        print()
        print("⚠️  清理不完整，请手动检查")
        sys.exit(1)

