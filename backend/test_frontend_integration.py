#!/usr/bin/env python3
"""
前端集成测试脚本
用于验证前端和后端的完整集成
"""

import requests
import json
import time

# API基础URL
BASE_URL = 'http://localhost:8000/api'

def test_jwt_authentication():
    """测试JWT认证流程"""
    print("🔐 测试JWT认证流程...")
    
    try:
        # 1. 获取JWT token
        print("   1. 获取JWT token...")
        response = requests.post(f'{BASE_URL}/token/', json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        if response.status_code != 200:
            print(f"   ❌ 获取token失败: {response.status_code}")
            return None
            
        data = response.json()
        access_token = data['access']
        refresh_token = data['refresh']
        
        print(f"   ✅ 获取token成功: {access_token[:20]}...")
        
        # 2. 使用token访问受保护的API
        print("   2. 测试受保护的API...")
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # 测试聊天API
        response = requests.post(f'{BASE_URL}/chat/sessions/create_session/', headers=headers)
        
        if response.status_code in [200, 201]:  # 200 OK 或 201 Created
            print("   ✅ 聊天API访问成功")
            session_data = response.json()
            print(f"      会话ID: {session_data['session']['id']}")
            return access_token
        else:
            print(f"   ❌ 聊天API访问失败: {response.status_code}")
            print(f"      响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ JWT认证测试失败: {e}")
        return None

def test_cors_headers():
    """测试CORS头部"""
    print("\n🌐 测试CORS配置...")
    
    try:
        # 测试预检请求
        response = requests.options(f'{BASE_URL}/chat/sessions/create_session/', headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'authorization,content-type'
        })
        
        if response.status_code == 200:
            print("   ✅ CORS预检请求成功")
            print(f"      Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
            print(f"      Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods')}")
            print(f"      Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers')}")
        else:
            print(f"   ❌ CORS预检请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ CORS测试失败: {e}")

def test_chat_flow(access_token):
    """测试完整的聊天流程"""
    print("\n💬 测试完整聊天流程...")
    
    if not access_token:
        print("   ❌ 没有有效的access token")
        return
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # 1. 创建聊天会话
        print("   1. 创建聊天会话...")
        response = requests.post(f'{BASE_URL}/chat/sessions/create_session/', headers=headers)
        
        if response.status_code != 200:
            print(f"   ❌ 创建会话失败: {response.status_code}")
            return
            
        session_data = response.json()
        session_id = session_data['session']['id']
        print(f"   ✅ 会话创建成功: ID={session_id}")
        
        # 2. 发送消息
        print("   2. 发送聊天消息...")
        message_data = {
            'session_id': session_id,
            'content': '这是一条测试消息',
            'content_type': 'text'
        }
        
        response = requests.post(f'{BASE_URL}/chat/messages/', headers=headers, json=message_data)
        
        if response.status_code == 201:
            print("   ✅ 消息发送成功")
            message_response = response.json()
            print(f"      消息ID: {message_response['message']['id']}")
        else:
            print(f"   ❌ 消息发送失败: {response.status_code}")
            print(f"      响应: {response.text}")
        
        # 3. 获取聊天历史
        print("   3. 获取聊天历史...")
        response = requests.get(f'{BASE_URL}/chat/messages/chat_history/?session_id={session_id}', headers=headers)
        
        if response.status_code == 200:
            print("   ✅ 聊天历史获取成功")
            history_data = response.json()
            print(f"      消息数量: {len(history_data['messages'])}")
        else:
            print(f"   ❌ 聊天历史获取失败: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 聊天流程测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始前端集成测试...")
    print("=" * 60)
    
    # 等待服务器启动
    time.sleep(2)
    
    # 测试JWT认证
    access_token = test_jwt_authentication()
    
    # 测试CORS
    test_cors_headers()
    
    # 测试聊天流程
    test_chat_flow(access_token)
    
    print("\n" + "=" * 60)
    print("🎉 前端集成测试完成！")
    
    if access_token:
        print("\n✅ 所有测试通过！前端应该能够正常与后端通信。")
        print("\n📝 下一步:")
        print("   1. 启动前端: npm run dev")
        print("   2. 使用 admin/admin123 登录")
        print("   3. 测试聊天功能")
    else:
        print("\n❌ 部分测试失败，请检查后端配置。")

if __name__ == '__main__':
    main()
