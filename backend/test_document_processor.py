#!/usr/bin/env python3
"""
测试文档处理功能
"""

import os
import sys
import django
from pathlib import Path

# 设置 Django 环境
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from document_processor.processors import get_processor, process_document
from document_processor.models import Document, DocumentChunk, LearningPackage


def test_processors():
    """测试文档处理器"""
    print("=== 测试文档处理器 ===")
    
    # 测试支持的格式
    test_files = [
        'test.pdf',
        'test.docx',
        'test.md',
        'test.txt'
    ]
    
    for test_file in test_files:
        try:
            processor = get_processor(test_file)
            print(f"✓ {test_file}: {processor.__class__.__name__}")
        except ValueError as e:
            print(f"✗ {test_file}: {e}")
    
    print()


def test_models():
    """测试数据模型"""
    print("=== 测试数据模型 ===")
    
    # 检查模型是否已创建
    try:
        doc_count = Document.objects.count()
        chunk_count = DocumentChunk.objects.count()
        package_count = LearningPackage.objects.count()
        
        print(f"✓ Document 模型: {doc_count} 条记录")
        print(f"✓ DocumentChunk 模型: {chunk_count} 条记录")
        print(f"✓ LearningPackage 模型: {package_count} 条记录")
        
    except Exception as e:
        print(f"✗ 模型测试失败: {e}")
    
    print()


def test_api_endpoints():
    """测试 API 端点"""
    print("=== 测试 API 端点 ===")
    
    from django.urls import reverse
    from django.test import Client
    
    client = Client()
    
    # 测试文档列表端点
    try:
        response = client.get('/api/documents/')
        print(f"✓ 文档列表端点: {response.status_code}")
    except Exception as e:
        print(f"✗ 文档列表端点: {e}")
    
    # 测试学习包端点
    try:
        response = client.get('/api/packages/')
        print(f"✓ 学习包端点: {response.status_code}")
    except Exception as e:
        print(f"✗ 学习包端点: {e}")
    
    print()


def main():
    """主函数"""
    print("开始测试文档处理功能...\n")
    
    test_processors()
    test_models()
    test_api_endpoints()
    
    print("测试完成！")


if __name__ == '__main__':
    main()
