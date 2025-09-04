#!/usr/bin/env python
"""
测试用户连接管理和主动触发功能
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from chat_system.proactive import proactive_engine

def test_user_connection_management():
    """测试用户连接管理"""
    print("🧪 测试用户连接管理功能")
    print("=" * 50)
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username='test_user_connection',
        defaults={'email': 'test@example.com'}
    )
    
    print(f"📋 测试用户: {user.username} (ID: {user.id})")
    
    # 测试添加用户连接
    print("\n1. 测试添加用户连接...")
    proactive_engine.add_connected_user(user.id, "test_session_123")
    print(f"✅ 用户 {user.id} 已添加到在线列表")
    
    # 检查用户是否在线
    print("\n2. 检查用户在线状态...")
    is_online = proactive_engine.is_user_online(user.id)
    print(f"📱 用户在线状态: {'在线' if is_online else '离线'}")
    
    # 获取在线用户列表
    print("\n3. 获取在线用户列表...")
    online_users = proactive_engine.get_online_users()
    print(f"👥 在线用户: {online_users}")
    
    # 测试发送消息给指定用户
    print("\n4. 测试向指定用户发送消息...")
    test_message = "这是一条测试主动消息！"
    success = proactive_engine.send_message_to_user(
        user.id, test_message, 'proactive'
    )
    print(f"📤 消息发送结果: {'成功' if success else '失败'}")
    
    # 测试向所有在线用户发送消息
    print("\n5. 测试向所有在线用户发送消息...")
    broadcast_message = "这是一条广播消息！"
    sent_count = proactive_engine.send_proactive_message_to_all_online(
        broadcast_message, 'proactive'
    )
    print(f"📢 广播消息发送给 {sent_count} 个用户")
    
    # 测试移除用户连接
    print("\n6. 测试移除用户连接...")
    proactive_engine.remove_connected_user(user.id)
    is_online_after = proactive_engine.is_user_online(user.id)
    print(f"📱 移除后用户在线状态: {'在线' if is_online_after else '离线'}")
    
    # 测试向离线用户发送消息
    print("\n7. 测试向离线用户发送消息...")
    success_offline = proactive_engine.send_message_to_user(
        user.id, "离线用户消息", 'proactive'
    )
    print(f"📤 向离线用户发送消息结果: {'成功' if success_offline else '失败（预期）'}")
    
    print("\n✅ 用户连接管理测试完成！")

def test_multiple_users():
    """测试多用户连接管理"""
    print("\n🧪 测试多用户连接管理")
    print("=" * 50)
    
    # 创建多个测试用户
    users = []
    for i in range(3):
        user, created = User.objects.get_or_create(
            username=f'test_user_{i+1}',
            defaults={'email': f'test{i+1}@example.com'}
        )
        users.append(user)
        proactive_engine.add_connected_user(user.id, f"session_{i+1}")
        print(f"👤 添加用户: {user.username} (ID: {user.id})")
    
    # 显示所有在线用户
    online_users = proactive_engine.get_online_users()
    print(f"\n📱 当前在线用户: {online_users}")
    
    # 向特定用户发送消息
    print(f"\n📤 向用户 {users[0].id} 发送个人消息...")
    success = proactive_engine.send_message_to_user(
        users[0].id, "这是给你的个人消息！", 'care'
    )
    print(f"发送结果: {'成功' if success else '失败'}")
    
    # 向所有用户广播消息
    print(f"\n📢 向所有用户广播消息...")
    sent_count = proactive_engine.send_proactive_message_to_all_online(
        "大家好！这是一条广播消息！", 'greeting'
    )
    print(f"广播发送给 {sent_count} 个用户")
    
    # 逐个移除用户
    print(f"\n👋 逐个移除用户...")
    for user in users:
        proactive_engine.remove_connected_user(user.id)
        print(f"移除用户: {user.username}")
    
    # 检查最终状态
    final_online = proactive_engine.get_online_users()
    print(f"\n📱 最终在线用户: {final_online}")
    
    print("\n✅ 多用户连接管理测试完成！")

def cleanup_test_users():
    """清理测试用户"""
    print("\n🧹 清理测试用户...")
    
    test_usernames = ['test_user_connection', 'test_user_1', 'test_user_2', 'test_user_3']
    
    for username in test_usernames:
        try:
            user = User.objects.get(username=username)
            user.delete()
            print(f"✅ 删除用户: {username}")
        except User.DoesNotExist:
            print(f"ℹ️  用户不存在: {username}")

def main():
    """主测试函数"""
    print("🚀 用户连接管理测试开始")
    print("=" * 60)
    
    try:
        test_user_connection_management()
        test_multiple_users()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试完成！")
        
        # 询问是否清理测试数据
        cleanup = input("\n🧹 是否清理测试用户？(y/N): ").lower().strip()
        if cleanup == 'y':
            cleanup_test_users()
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 测试结束")

if __name__ == "__main__":
    main()
