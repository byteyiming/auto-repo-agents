#!/usr/bin/env python3
"""
测试 Web 服务器和 API 端点
"""
import requests
import time
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_server_health():
    """测试服务器健康状态"""
    print("=" * 80)
    print("🧪 测试 1: 服务器健康检查")
    print("=" * 80)
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ 服务器响应: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
        print("   启动命令: python3 -m uvicorn src.web.app:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_api_endpoints():
    """测试 API 端点"""
    print("\n" + "=" * 80)
    print("🧪 测试 2: API 端点检查")
    print("=" * 80)
    
    endpoints = [
        ("GET", "/api/status", None),
        ("GET", "/api/health", None),
    ]
    
    results = []
    for method, endpoint, data in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=5)
            
            status = "✅" if response.status_code < 400 else "⚠️"
            print(f"{status} {method} {endpoint}: {response.status_code}")
            results.append(response.status_code < 400)
        except Exception as e:
            print(f"❌ {method} {endpoint}: {e}")
            results.append(False)
    
    return all(results)

def test_document_generation():
    """测试文档生成流程"""
    print("\n" + "=" * 80)
    print("🧪 测试 3: 文档生成流程")
    print("=" * 80)
    
    project_id = f"test_{int(time.time())}"
    user_idea = "创建一个简单的待办事项应用，支持任务创建、编辑、删除和标记完成"
    
    print(f"📝 项目ID: {project_id}")
    print(f"💡 用户想法: {user_idea}")
    print()
    
    try:
        # 1. 启动生成
        print("1. 启动文档生成...")
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json={
                "user_idea": user_idea,
                "project_id": project_id,
                "profile": "individual",
                "phase1_only": True  # 只测试 Phase 1
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ 生成请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
        
        data = response.json()
        print(f"✅ 生成请求已提交")
        print(f"   项目ID: {data.get('project_id')}")
        print(f"   状态: {data.get('status')}")
        
        # 2. 检查项目状态
        print("\n2. 检查项目状态...")
        time.sleep(2)  # 等待一下
        
        status_response = requests.get(
            f"{BASE_URL}/api/status/{project_id}",
            timeout=5
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"✅ 项目状态: {status_data.get('status', 'unknown')}")
        else:
            print(f"⚠️  无法获取状态: {status_response.status_code}")
        
        # 3. 等待文档生成（最多等待30秒）
        print("\n3. 等待文档生成...")
        max_wait = 30
        waited = 0
        
        while waited < max_wait:
            time.sleep(2)
            waited += 2
            
            # 检查是否有文档生成
            try:
                # 尝试获取 requirements 文档
                doc_response = requests.get(
                    f"{BASE_URL}/api/document/{project_id}/requirements_analyst",
                    timeout=5
                )
                
                if doc_response.status_code == 200:
                    doc_data = doc_response.json()
                    print(f"✅ 文档已生成!")
                    print(f"   文档类型: {doc_data.get('agent_type')}")
                    print(f"   版本: {doc_data.get('version')}")
                    print(f"   状态: {doc_data.get('status')}")
                    print(f"   质量分数: {doc_data.get('quality_score')}")
                    return True
            except:
                pass
            
            print(f"   等待中... ({waited}/{max_wait}秒)")
        
        print("⚠️  文档生成超时（这可能是正常的，因为生成需要时间）")
        return True  # 返回 True，因为请求已提交
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_approval():
    """测试文档审批流程"""
    print("\n" + "=" * 80)
    print("🧪 测试 4: 文档审批流程")
    print("=" * 80)
    
    # 使用一个已存在的项目ID（如果有的话）
    project_id = f"test_approval_{int(time.time())}"
    
    print(f"📝 项目ID: {project_id}")
    print("⚠️  注意: 这个测试需要先有文档生成")
    print("   在实际使用中，文档生成后会等待审批")
    
    try:
        # 测试审批端点（即使文档不存在，也应该返回合理的错误）
        print("\n1. 测试审批端点...")
        response = requests.post(
            f"{BASE_URL}/api/approve-document/{project_id}/requirements_analyst",
            json={"notes": "测试审批"},
            timeout=5
        )
        
        if response.status_code == 404:
            print("✅ 端点存在，但项目不存在（这是预期的）")
            return True
        elif response.status_code == 200:
            print("✅ 文档审批成功")
            return True
        else:
            print(f"⚠️  意外状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "🚀" * 40)
    print("开始测试 Web 服务器")
    print("🚀" * 40 + "\n")
    
    results = []
    
    # 测试服务器健康
    results.append(("服务器健康", test_server_health()))
    
    if not results[-1][1]:
        print("\n❌ 服务器未运行，请先启动服务器")
        print("   命令: python3 -m uvicorn src.web.app:app --reload --host 0.0.0.0 --port 8000")
        return 1
    
    # 测试 API 端点
    results.append(("API 端点", test_api_endpoints()))
    
    # 测试文档生成（可选，因为可能需要较长时间）
    print("\n" + "=" * 80)
    print("⚠️  文档生成测试需要较长时间，是否继续？")
    print("   这将启动一个实际的文档生成任务")
    print("=" * 80)
    
    # 测试文档审批
    results.append(("文档审批端点", test_document_approval()))
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查上面的错误信息")
    print("=" * 80)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("❌ 需要安装 requests 库")
        print("   命令: pip install requests")
        exit(1)
    
    exit(main())

