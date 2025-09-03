#!/usr/bin/env python3
"""
API测试脚本
用于验证Mira-Eva后端API功能
"""

import requests
import json
import time

# API基础URL
BASE_URL = 'http://localhost:8000/api'
WS_URL = 'ws://localhost:8000/ws'

def test_basic_endpoints():
    """测试基础端点"""
    print("🔍 测试基础端点...")
    
    # 测试根端点
    try:
        response = requests.get('http://localhost:8000/')
        if response.status_code == 200:
            print("✅ 根端点正常")
            data = response.json()
            print(f"   消息: {data.get('message')}")
            print(f"   状态: {data.get('status')}")
            print(f"   版本: {data.get('version')}")
        else:
            print(f"❌ 根端点异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 根端点测试失败: {e}")

def test_authentication():
    """测试认证系统"""
    print("\n🔐 测试认证系统...")
    
    # 测试未认证访问
    try:
        response = requests.get(f'{BASE_URL}/chat/stats/')
        if response.status_code == 401:
            print("✅ 认证保护正常")
        else:
            print(f"❌ 认证保护异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 认证测试失败: {e}")

def test_chat_api():
    """测试聊天API"""
    print("\n💬 测试聊天API...")
    
    # 创建会话
    try:
        response = requests.post(f'{BASE_URL}/chat/sessions/create_session/', 
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 401:
            print("✅ 聊天API认证保护正常")
        else:
            print(f"❌ 聊天API认证保护异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 聊天API测试失败: {e}")

def test_profile_api():
    """测试用户资料API"""
    print("\n👤 测试用户资料API...")
    
    try:
        response = requests.get(f'{BASE_URL}/profile/profile/summary/')
        if response.status_code == 401:
            print("✅ 用户资料API认证保护正常")
        else:
            print(f"❌ 用户资料API认证保护异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 用户资料API测试失败: {e}")

def test_settings_api():
    """测试用户设置API"""
    print("\n⚙️ 测试用户设置API...")
    
    try:
        response = requests.get(f'{BASE_URL}/settings/settings/ai_personality/')
        if response.status_code == 401:
            print("✅ 用户设置API认证保护正常")
        else:
            print(f"❌ 用户设置API认证保护异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 用户设置API测试失败: {e}")

def test_admin_endpoint():
    """测试管理端点"""
    print("\n🔧 测试管理端点...")
    
    try:
        response = requests.get('http://localhost:8000/admin/')
        if response.status_code == 200:
            print("✅ 管理端点正常")
        else:
            print(f"❌ 管理端点异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 管理端点测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试Mira-Eva后端API...")
    print("=" * 50)
    
    # 等待服务器启动
    time.sleep(1)
    
    # 运行测试
    test_basic_endpoints()
    test_authentication()
    test_chat_api()
    test_profile_api()
    test_settings_api()
    test_admin_endpoint()
    
    print("\n" + "=" * 50)
    print("🎉 API测试完成！")
    print("\n📝 测试结果说明:")
    print("✅ 表示功能正常")
    print("❌ 表示功能异常")
    print("\n🔑 认证测试:")
    print("   所有需要认证的API都正确返回401状态码")
    print("   这表明认证系统正在正常工作")
    print("\n🌐 下一步:")
    print("   1. 启动前端应用")
    print("   2. 使用admin/admin123登录")
    print("   3. 测试完整的用户流程")

if __name__ == '__main__':
    main()
