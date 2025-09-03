#!/usr/bin/env python3
"""
测试完整的文档处理系统
"""

import os
import sys
import django
from pathlib import Path
import requests
import json

# 设置 Django 环境
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def create_test_user():
    """创建测试用户"""
    try:
        user = User.objects.get(username='testuser')
        print("✓ 测试用户已存在")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print("✓ 测试用户创建成功")
    
    return user


def get_auth_token(user):
    """获取认证令牌"""
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    print("✓ 认证令牌获取成功")
    return access_token


def test_api_endpoints(base_url, headers):
    """测试 API 端点"""
    print("\n=== 测试 API 端点 ===")
    
    # 测试文档列表
    try:
        response = requests.get(f"{base_url}/api/documents/", headers=headers)
        print(f"✓ 文档列表: {response.status_code}")
    except Exception as e:
        print(f"✗ 文档列表: {e}")
    
    # 测试学习包列表
    try:
        response = requests.get(f"{base_url}/api/packages/", headers=headers)
        print(f"✓ 学习包列表: {response.status_code}")
    except Exception as e:
        print(f"✗ 学习包列表: {e}")
    
    # 测试根端点
    try:
        response = requests.get(f"{base_url}/", headers=headers)
        print(f"✓ 根端点: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  支持的功能: {list(data.get('endpoints', {}).keys())}")
    except Exception as e:
        print(f"✗ 根端点: {e}")


def test_document_upload(base_url, headers):
    """测试文档上传"""
    print("\n=== 测试文档上传 ===")
    
    # 创建测试 Markdown 文件
    test_content = """# 测试文档
这是一个测试文档，用于验证文档处理系统。

## 测试内容
- 第一点
- 第二点
- 第三点

## 对话示例
> "你好，今天天气怎么样？"
> "天气很好，适合出去走走。"

## 总结
这是一个包含多种内容类型的测试文档。
"""
    
    test_file_path = "test_upload.md"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        with open(test_file_path, "rb") as f:
            files = {'file': ('test_upload.md', f, 'text/markdown')}
            data = {'title': '测试文档'}
            
            response = requests.post(
                f"{base_url}/api/documents/",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 201:
                result = response.json()
                print("✓ 文档上传成功")
                print(f"  文档ID: {result.get('document', {}).get('id')}")
                print(f"  状态: {result.get('document', {}).get('status')}")
                
                # 获取文档详情
                doc_id = result['document']['id']
                detail_response = requests.get(
                    f"{base_url}/api/documents/{doc_id}/",
                    headers=headers
                )
                
                if detail_response.status_code == 200:
                    doc_detail = detail_response.json()
                    print(f"  提取文本长度: {len(doc_detail.get('extracted_text', ''))}")
                    print(f"  分块数量: {len(doc_detail.get('chunks', []))}")
                    
                    # 显示分块信息
                    for i, chunk in enumerate(doc_detail.get('chunks', [])[:3]):
                        print(f"    分块 {i+1}: {chunk.get('chunk_type')} - {chunk.get('content', '')[:50]}...")
                
            else:
                print(f"✗ 文档上传失败: {response.status_code}")
                print(f"  错误: {response.text}")
                
    except Exception as e:
        print(f"✗ 文档上传测试失败: {e}")
    
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)


def test_learning_package(base_url, headers):
    """测试学习包创建"""
    print("\n=== 测试学习包创建 ===")
    
    try:
        # 先获取文档列表
        docs_response = requests.get(f"{base_url}/api/documents/", headers=headers)
        if docs_response.status_code == 200:
            documents = docs_response.json()
            if documents and len(documents) > 0:
                doc_id = documents[0]['id']
                
                # 创建学习包
                package_data = {
                    'name': '测试学习包',
                    'description': '这是一个测试学习包',
                    'package_type': 'conversation',
                    'document_ids': [doc_id]
                }
                
                response = requests.post(
                    f"{base_url}/api/packages/",
                    json=package_data,
                    headers={**headers, 'Content-Type': 'application/json'}
                )
                
                if response.status_code == 201:
                    result = response.json()
                    print("✓ 学习包创建成功")
                    print(f"  包ID: {result.get('package', {}).get('id')}")
                    print(f"  名称: {result.get('package', {}).get('name')}")
                    print(f"  类型: {result.get('package', {}).get('package_type')}")
                else:
                    print(f"✗ 学习包创建失败: {response.status_code}")
                    print(f"  错误: {response.text}")
            else:
                print("⚠ 没有可用的文档来创建学习包")
        else:
            print(f"✗ 获取文档列表失败: {docs_response.status_code}")
            
    except Exception as e:
        print(f"✗ 学习包测试失败: {e}")


def main():
    """主函数"""
    print("开始测试完整的文档处理系统...\n")
    
    # 创建测试用户
    user = create_test_user()
    
    # 获取认证令牌
    token = get_auth_token(user)
    
    # 设置基础 URL 和请求头
    base_url = "http://localhost:8000"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    
    print(f"\n使用认证令牌: {token[:20]}...")
    
    # 测试 API 端点
    test_api_endpoints(base_url, headers)
    
    # 测试文档上传
    test_document_upload(base_url, headers)
    
    # 测试学习包创建
    test_learning_package(base_url, headers)
    
    print("\n=== 测试完成 ===")
    print("如果所有测试都通过，说明系统运行正常！")
    print(f"前端页面: http://localhost:5173/documents")
    print(f"后端API: {base_url}/api/")


if __name__ == '__main__':
    main()
