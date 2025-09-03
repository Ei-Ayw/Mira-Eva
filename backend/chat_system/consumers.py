import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatSession, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.user = self.scope['user']
        if not await self.verify_session():
            await self.close()
            return
        await self.channel_layer.group_add(f"chat_{self.session_id}", self.channel_name)
        await self.accept()
        await self.send(json.dumps({
            'type': 'connection_established', 'session_id': self.session_id
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(f"chat_{self.session_id}", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'chat_message':
            content = data.get('content', '')
            content_type = data.get('content_type', 'text')
            msg = await self.save_message(content, content_type)
            await self.channel_layer.group_send(
                f"chat_{self.session_id}",
                {'type': 'chat_message', 'message': {
                    'id': msg.id, 'content': msg.content, 'content_type': msg.content_type,
                    'sender': 'user', 'timestamp': msg.timestamp.isoformat()
                }}
            )

    async def chat_message(self, event):
        await self.send(json.dumps({'type': 'chat_message', 'message': event['message']}))

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


