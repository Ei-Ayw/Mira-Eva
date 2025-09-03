#!/usr/bin/env python3
"""
文档处理系统演示脚本
"""

import os
import sys
import django
from pathlib import Path

# 设置 Django 环境
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from document_processor.models import Document, DocumentChunk, LearningPackage
from django.contrib.auth.models import User


def show_system_status():
    """显示系统状态"""
    print("=" * 60)
    print("📚 Mira-Eva 文档处理系统状态")
    print("=" * 60)
    
    # 统计信息
    total_docs = Document.objects.count()
    total_chunks = DocumentChunk.objects.count()
    total_packages = LearningPackage.objects.count()
    total_users = User.objects.count()
    
    print(f"👥 用户总数: {total_users}")
    print(f"📄 文档总数: {total_docs}")
    print(f"🔖 内容分块: {total_chunks}")
    print(f"📦 学习包: {total_packages}")
    print()


def show_documents():
    """显示文档列表"""
    print("📄 文档列表:")
    print("-" * 40)
    
    documents = Document.objects.all().order_by('-created_at')
    
    if not documents:
        print("  暂无文档")
        return
    
    for doc in documents:
        status_emoji = {
            'uploading': '⏳',
            'processing': '⚙️',
            'completed': '✅',
            'failed': '❌'
        }.get(doc.status, '❓')
        
        print(f"  {status_emoji} {doc.title}")
        print(f"     类型: {doc.get_file_type_display()}")
        print(f"     大小: {doc.file_size / (1024 * 1024):.2f} MB")
        print(f"     状态: {doc.get_status_display()}")
        print(f"     上传时间: {doc.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        if doc.status == 'completed':
            chunks = doc.chunks.all()
            print(f"     分块数量: {chunks.count()}")
            
            # 显示分块类型统计
            chunk_types = {}
            for chunk in chunks:
                chunk_type = chunk.get_chunk_type_display()
                chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
            
            if chunk_types:
                type_str = ", ".join([f"{k}: {v}" for k, v in chunk_types.items()])
                print(f"     分块类型: {type_str}")
        
        print()
    
    print()


def show_learning_packages():
    """显示学习包列表"""
    print("📦 学习包列表:")
    print("-" * 40)
    
    packages = LearningPackage.objects.all().order_by('-created_at')
    
    if not packages:
        print("  暂无学习包")
        return
    
    for pkg in packages:
        type_emoji = {
            'conversation': '💬',
            'knowledge': '🧠',
            'training': '🎯',
            'reference': '📚'
        }.get(pkg.package_type, '📦')
        
        print(f"  {type_emoji} {pkg.name}")
        print(f"     类型: {pkg.get_package_type_display()}")
        print(f"     描述: {pkg.description or '无描述'}")
        print(f"     文档数: {pkg.documents.count()}")
        print(f"     分块数: {pkg.total_chunks}")
        print(f"     示例数: {pkg.total_examples}")
        print(f"     创建时间: {pkg.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # 显示包含的文档
        if pkg.documents.exists():
            doc_names = [doc.title for doc in pkg.documents.all()]
            print(f"     包含文档: {', '.join(doc_names[:3])}")
            if len(doc_names) > 3:
                print(f"               ... 还有 {len(doc_names) - 3} 个文档")
        
        print()
    
    print()


def show_sample_content():
    """显示示例内容"""
    print("🔍 内容示例:")
    print("-" * 40)
    
    # 查找一个已完成的文档
    doc = Document.objects.filter(status='completed').first()
    if not doc:
        print("  暂无已处理的文档")
        return
    
    print(f"📄 文档: {doc.title}")
    print(f"   提取的文本长度: {len(doc.extracted_text)} 字符")
    print(f"   摘要: {doc.summary}")
    
    if doc.keywords:
        print(f"   关键词: {', '.join(doc.keywords)}")
    
    print("\n   分块内容:")
    
    chunks = doc.chunks.all().order_by('order')
    for i, chunk in enumerate(chunks[:5], 1):  # 只显示前5个分块
        print(f"\n   {i}. [{chunk.get_chunk_type_display()}]")
        content = chunk.content
        if len(content) > 100:
            content = content[:100] + "..."
        print(f"      {content}")
    
    if chunks.count() > 5:
        print(f"\n   ... 还有 {chunks.count() - 5} 个分块")
    
    print()


def show_api_endpoints():
    """显示 API 端点信息"""
    print("🔗 API 端点:")
    print("-" * 40)
    
    endpoints = [
        ("📄 文档管理", "/api/documents/"),
        ("📦 学习包管理", "/api/packages/"),
        ("💬 聊天系统", "/api/chat/"),
        ("👤 用户资料", "/api/profile/"),
        ("⚙️ 用户设置", "/api/settings/"),
        ("🤖 AI 引擎", "/api/ai/"),
        ("🔐 认证", "/api/token/"),
        ("📡 WebSocket", "/ws/chat/{session_id}/"),
    ]
    
    for name, endpoint in endpoints:
        print(f"  {name:<15} {endpoint}")
    
    print()


def main():
    """主函数"""
    print("🚀 启动 Mira-Eva 文档处理系统演示...\n")
    
    try:
        show_system_status()
        show_documents()
        show_learning_packages()
        show_sample_content()
        show_api_endpoints()
        
        print("=" * 60)
        print("🎉 演示完成！")
        print("=" * 60)
        print("\n💡 使用提示:")
        print("  1. 前端页面: http://localhost:5173/documents")
        print("  2. 后端API: http://localhost:8000/api/")
        print("  3. 系统状态: http://localhost:8000/")
        print("\n📝 可以上传以下格式的文档进行测试:")
        print("  - PDF (.pdf)")
        print("  - Word (.docx, .doc)")
        print("  - Markdown (.md, .markdown)")
        print("  - 纯文本 (.txt)")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()










