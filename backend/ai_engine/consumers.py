"""
WebSocket消费者
处理实时聊天连接和消息
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    """聊天WebSocket消费者"""
    
    async def connect(self):
        """建立WebSocket连接"""
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        # 获取用户信息
        self.user = self.scope['user']
        
        if isinstance(self.user, AnonymousUser):
            # 未认证用户拒绝连接
            await self.close()
            return
        
        # 加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"用户 {self.user.username} 连接到聊天室 {self.conversation_id}")
        
        # 发送连接成功消息
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': '连接成功',
            'user': self.user.username,
            'conversation_id': self.conversation_id
        }))
    
    async def disconnect(self, close_code):
        """断开WebSocket连接"""
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"用户 {self.user.username} 断开连接，代码: {close_code}")
    
    async def receive(self, text_data):
        """接收WebSocket消息"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'chat_message')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read_receipt':
                await self.handle_read_receipt(data)
            else:
                logger.warning(f"未知消息类型: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("无效的JSON数据")
        except Exception as e:
            logger.error(f"处理WebSocket消息时出错: {str(e)}")
    
    async def handle_chat_message(self, data):
        """处理聊天消息"""
        content = data.get('content', '')
        message_type = data.get('message_type', 'text')
        metadata = data.get('metadata', {})
        
        if not content:
            return
        
        # 保存消息到数据库
        message = await self.save_message(content, message_type, metadata)
        
        # 广播消息到房间组
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'content': content,
                    'message_type': message_type,
                    'sender': 'user',
                    'user': self.user.username,
                    'timestamp': message.timestamp.isoformat(),
                    'metadata': metadata
                }
            }
        )
        
        # 生成AI回复
        ai_response = await self.generate_ai_response(content, message_type, metadata)
        
        # 广播AI回复到房间组
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'ai_response',
                'message': ai_response
            }
        )
    
    async def handle_typing(self, data):
        """处理正在输入状态"""
        is_typing = data.get('is_typing', False)
        
        # 广播输入状态到房间组
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing',
                'user': self.user.username,
                'is_typing': is_typing
            }
        )
    
    async def handle_read_receipt(self, data):
        """处理已读回执"""
        message_id = data.get('message_id')
        
        if message_id:
            # 标记消息为已读
            await self.mark_message_as_read(message_id)
            
            # 广播已读回执到房间组
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'read_receipt',
                    'message_id': message_id,
                    'user': self.user.username
                }
            )
    
    async def chat_message(self, event):
        """发送聊天消息到WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))
    
    async def ai_response(self, event):
        """发送AI回复到WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'ai_response',
            'message': event['message']
        }))
    
    async def user_typing(self, event):
        """发送用户输入状态到WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'user': event['user'],
            'is_typing': event['is_typing']
        }))
    
    async def read_receipt(self, event):
        """发送已读回执到WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'user': event['user']
        }))
    
    @database_sync_to_async
    def save_message(self, content, message_type, metadata):
        """保存消息到数据库"""
        from .models import AIConversation, AIMessage
        
        # 获取或创建对话会话
        conversation, created = AIConversation.objects.get_or_create(
            user=self.user,
            session_id=self.conversation_id,
            defaults={
                'ai_name': 'Mira',
                'ai_avatar': '/images/ai-avatar.png'
            }
        )
        
        # 创建消息
        message = AIMessage.objects.create(
            conversation=conversation,
            message_type=message_type,
            sender='user',
            content=content,
            metadata=metadata
        )
        
        return message
    
    @database_sync_to_async
    def generate_ai_response(self, content, message_type, metadata):
        """生成AI回复"""
        from .core import AIEngine
        
        # 初始化AI引擎
        ai_engine = AIEngine()
        
        # 生成回复
        response = ai_engine.process_user_input(
            user_id=self.user.id,
            input_data={
                'content': content,
                'message_type': message_type,
                'metadata': metadata
            }
        )
        
        if response.get('success', False):
            # 保存AI回复到数据库
            from .models import AIMessage, AIResponse
            
            conversation = AIConversation.objects.get(
                user=self.user,
                session_id=self.conversation_id
            )
            
            ai_message = AIMessage.objects.create(
                conversation=conversation,
                message_type=response.get('type', 'text'),
                sender='ai',
                content=response.get('content', ''),
                content_url=response.get('content_url', ''),
                metadata={
                    'intent': response.get('intent', ''),
                    'emotion': response.get('emotion', ''),
                    'confidence': response.get('confidence', 0.8),
                    'response_time': response.get('response_time', 0)
                }
            )
            
            AIResponse.objects.create(
                message=ai_message,
                response_content=response.get('content', ''),
                response_type=response.get('type', 'text'),
                response_url=response.get('content_url', ''),
                confidence_score=response.get('confidence', 0.8),
                response_time=response.get('response_time', 0),
                model_used='virtual'
            )
            
            return {
                'id': ai_message.id,
                'content': response.get('content', ''),
                'message_type': response.get('type', 'text'),
                'sender': 'ai',
                'user': 'Mira',
                'timestamp': ai_message.timestamp.isoformat(),
                'metadata': response.get('metadata', {})
            }
        else:
            return {
                'id': None,
                'content': '抱歉，我现在有点忙，稍后再和你聊天吧～',
                'message_type': 'text',
                'sender': 'ai',
                'user': 'Mira',
                'timestamp': None,
                'metadata': {}
            }
    
    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        """标记消息为已读"""
        from .models import AIMessage
        
        try:
            message = AIMessage.objects.get(id=message_id)
            message.is_read = True
            message.save()
        except AIMessage.DoesNotExist:
            logger.warning(f"消息不存在: {message_id}")
