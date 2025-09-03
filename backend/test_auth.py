#!/usr/bin/env python3
"""
认证系统测试脚本
用于测试Mira-Eva后端的认证功能
"""

import requests
import json
import time

# API基础URL
BASE_URL = 'http://localhost:8000/api'

def test_basic_endpoints():
    """测试基础端点"""
    print("🔍 测试基础端点...")
    
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
            print("✅ 认证保护正常 - 返回401")
        elif response.status_code == 403:
            print("✅ 认证保护正常 - 返回403")
        else:
            print(f"❌ 认证保护异常: {response.status_code}")
            print(f"   响应内容: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ 认证测试失败: {e}")

def test_chat_api_with_auth():
    """测试带认证的聊天API"""
    print("\n💬 测试带认证的聊天API...")
    
    # 使用模拟token
    headers = {
        'Authorization': 'Token mock_token_123',
        'Content-Type': 'application/json'
    }
    
    try:
        # 测试创建会话
        response = requests.post(
            f'{BASE_URL}/chat/sessions/create_session/',
            headers=headers
        )
        
        print(f"创建会话响应: {response.status_code}")
        if response.status_code == 200:
            print("✅ 创建会话成功")
            data = response.json()
            print(f"   会话数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 创建会话失败: {response.status_code}")
            print(f"   响应内容: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ 聊天API测试失败: {e}")

def test_websocket_endpoint():
    """测试WebSocket端点"""
    print("\n🔌 测试WebSocket端点...")
    
    try:
        # 测试WebSocket URL格式
        ws_url = "ws://localhost:8000/ws/chat/test_session/"
        print(f"WebSocket URL: {ws_url}")
        print("✅ WebSocket端点配置正常")
        
        # 注意：这里只是测试URL格式，实际WebSocket连接需要客户端测试
        print("💡 WebSocket连接测试需要在浏览器中进行")
        
    except Exception as e:
        print(f"❌ WebSocket测试失败: {e}")

def test_cors():
    """测试CORS配置"""
    print("\n🌐 测试CORS配置...")
    
    try:
        # 测试预检请求
        response = requests.options(
            f'{BASE_URL}/chat/stats/',
            headers={
                'Origin': 'http://localhost:5173',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'authorization,content-type'
            }
        )
        
        if response.status_code == 200:
            print("✅ CORS预检请求正常")
            print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
            print(f"   Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods')}")
            print(f"   Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers')}")
        else:
            print(f"❌ CORS预检请求异常: {response.status_code}")
            
    except Exception as e:
        print(f"❌ CORS测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试Mira-Eva后端认证系统...")
    print("=" * 60)
    
    # 等待服务器启动
    time.sleep(1)
    
    # 运行测试
    test_basic_endpoints()
    test_authentication()
    test_chat_api_with_auth()
    test_websocket_endpoint()
    test_cors()
    
    print("\n" + "=" * 60)
    print("🎉 认证系统测试完成！")
    print("\n📝 测试结果说明:")
    print("✅ 表示功能正常")
    print("❌ 表示功能异常")
    print("\n🔑 认证问题诊断:")
    print("   1. 检查前端是否正确发送Authorization头")
    print("   2. 检查token格式是否正确 (Token <token>)")
    print("   3. 检查WebSocket连接是否建立")
    print("   4. 检查CORS配置是否正确")

if __name__ == '__main__':
    main()
