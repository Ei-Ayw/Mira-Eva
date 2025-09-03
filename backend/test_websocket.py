#!/usr/bin/env python3
"""
WebSocket连接测试脚本
用于测试Mira-Eva后端的WebSocket功能
"""

import asyncio
import websockets
import json
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_websocket_connection():
    """测试WebSocket连接"""
    uri = "ws://localhost:8000/ws/chat/1/"
    
    try:
        logger.info(f"尝试连接到WebSocket: {uri}")
        
        async with websockets.connect(uri) as websocket:
            logger.info("WebSocket连接成功！")
            
            # 发送测试消息
            test_message = {
                "type": "chat_message",
                "content": "这是一条测试消息",
                "message_type": "text"
            }
            
            logger.info(f"发送测试消息: {test_message}")
            await websocket.send(json.dumps(test_message))
            
            # 等待响应
            logger.info("等待响应...")
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                logger.info(f"收到响应: {response}")
            except asyncio.TimeoutError:
                logger.warning("等待响应超时")
            
            # 保持连接一段时间
            await asyncio.sleep(5)
            
    except Exception as e:
        logger.error(f"WebSocket连接失败: {e}")

async def test_multiple_messages():
    """测试发送多条消息"""
    uri = "ws://localhost:8000/ws/chat/1/"
    
    try:
        logger.info(f"尝试连接到WebSocket: {uri}")
        
        async with websockets.connect(uri) as websocket:
            logger.info("WebSocket连接成功！")
            
            # 发送多条测试消息
            test_messages = [
                {
                    "type": "chat_message",
                    "content": "第一条测试消息",
                    "message_type": "text"
                },
                {
                    "type": "chat_message",
                    "content": "第二条测试消息",
                    "message_type": "text"
                },
                {
                    "type": "typing",
                    "is_typing": True
                }
            ]
            
            for i, message in enumerate(test_messages):
                logger.info(f"发送消息 {i+1}: {message}")
                await websocket.send(json.dumps(message))
                await asyncio.sleep(2)
                
                # 尝试接收响应
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    logger.info(f"收到响应 {i+1}: {response}")
                except asyncio.TimeoutError:
                    logger.warning(f"消息 {i+1} 响应超时")
            
            # 保持连接一段时间
            await asyncio.sleep(3)
            
    except Exception as e:
        logger.error(f"WebSocket测试失败: {e}")

async def main():
    """主函数"""
    logger.info("🚀 开始WebSocket连接测试...")
    
    # 测试基本连接
    await test_websocket_connection()
    
    logger.info("\n" + "="*50)
    
    # 测试多条消息
    await test_multiple_messages()
    
    logger.info("\n🎉 WebSocket测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
