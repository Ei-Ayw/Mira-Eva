import json
import logging
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatSession, Message
from .proactive import proactive_engine

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.user = self.scope['user']
        self._owner_user_id = None
        self._owner_username = None
        if not await self.verify_session():
            await self.close()
            return
        
        # 添加到聊天组
        await self.channel_layer.group_add(f"chat_{self.session_id}", self.channel_name)
        
        # 解析会话所属用户（用于主动触发）
        owner_id, owner_username = await self.get_session_owner()
        self._owner_user_id = owner_id
        self._owner_username = owner_username

        # 添加到用户组（用于主动触发消息）
        if owner_id is not None:
            await self.channel_layer.group_add(f"chat_{owner_id}", self.channel_name)
            # 通知主动触发引擎用户已连接
            proactive_engine.add_connected_user(owner_id, self.session_id)
            logger.info(f"用户 {owner_username} (ID: {owner_id}) 已连接WebSocket（由会话归属识别）")
            # 连接即问候（带冷却）
            await sync_to_async(proactive_engine.send_welcome_on_connect)(owner_id)
        
        await self.accept()
        await self.send(json.dumps({
            'type': 'connection_established', 
            'session_id': self.session_id,
            'user_id': (self.user.id if getattr(self.user, 'is_authenticated', False) else None) or owner_id
        }))

    async def disconnect(self, close_code):
        # 从聊天组移除
        await self.channel_layer.group_discard(f"chat_{self.session_id}", self.channel_name)
        
        # 从用户组移除并通知主动触发引擎
        target_user_id = None
        if getattr(self.user, 'is_authenticated', False):
            target_user_id = self.user.id
        if self._owner_user_id is not None:
            target_user_id = self._owner_user_id
        if target_user_id is not None:
            await self.channel_layer.group_discard(f"chat_{target_user_id}", self.channel_name)
            proactive_engine.remove_connected_user(target_user_id)
            logger.info(f"用户(ID: {target_user_id}) 已断开WebSocket")

    async def receive(self, text_data):
        data = json.loads(text_data)
        # 心跳
        if data.get('type') == 'ping':
            await self.send(json.dumps({'type': 'pong', 'ts': data.get('ts')}))
            return
        if data.get('type') == 'chat_message':
            # 改为仅作为上行通道，不再在WS端保存与广播用户消息，避免与REST重复
            # 用户侧入库与AI回复由REST负责
            return

    async def chat_message(self, event):
        # 统一规范字段命名，补充缺失的字段，便于前端去重
        msg = event['message']
        payload = {
            'type': 'chat_message',
            'message': {
                'id': msg.get('id'),
                'content': msg.get('content'),
                'content_type': msg.get('content_type', 'text'),
                'sender': msg.get('sender', 'ai'),
                'timestamp': msg.get('timestamp')
            }
        }
        await self.send(json.dumps(payload))

    @database_sync_to_async
    def verify_session(self):
        try:
            sid = str(self.session_id)
            if sid.isdigit():
                ChatSession.objects.get(id=int(sid))
            else:
                ChatSession.objects.get(session_id=sid)
            return True
        except ChatSession.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content, content_type):
        sid = str(self.session_id)
        if sid.isdigit():
            session = ChatSession.objects.get(id=int(sid))
        else:
            session = ChatSession.objects.get(session_id=sid)
        return Message.objects.create(session=session, content=content, content_type=content_type, sender='user')

    @database_sync_to_async
    def get_session_owner(self):
        """返回会话所属用户 (id, username)；若异常返回 (None, None)"""
        try:
            sid = str(self.session_id)
            if sid.isdigit():
                session = ChatSession.objects.get(id=int(sid))
            else:
                session = ChatSession.objects.get(session_id=sid)
            user = session.user
            return user.id, getattr(user, 'username', None)
        except Exception:
            return None, None


