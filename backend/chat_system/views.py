import uuid
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ChatSession, Message
from .serializers import ChatSessionSerializer, MessageSerializer
from ai_engine.prompt_library import get_system_prompt, get_style_notes
from ai_engine.tencent_client import TencentDeepSeekClient


class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user, is_active=True).order_by('-updated_at')

    @action(detail=False, methods=['get'])
    def latest_or_create(self, request):
        user = request.user
        session = ChatSession.objects.filter(user=user, is_active=True).order_by('-updated_at').first()
        if not session:
            session = ChatSession.objects.create(
                user=user,
                session_id=f"session_{user.id}_{uuid.uuid4().hex[:8]}",
                is_active=True,
                created_at=timezone.now(),
            )
            Message.objects.create(session=session, content="你好！我是Mira，继续聊聊吗～", content_type='text', sender='ai')
        data = {'success': True, 'session': ChatSessionSerializer(session).data}
        if request.query_params.get('messages'):
            last_msgs = Message.objects.filter(session=session).order_by('-timestamp')[:50]
            data['messages'] = MessageSerializer(reversed(list(last_msgs)), many=True).data
        return Response(data)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        session_id = request.data.get('session_id')
        content = request.data.get('content', '')
        content_type = request.data.get('content_type', 'text')
        try:
            session = ChatSession.objects.get(id=session_id, user=user, is_active=True)
        except ChatSession.DoesNotExist:
            return Response({'success': False, 'message': '会话不存在或无权限'}, status=status.HTTP_404_NOT_FOUND)

        user_msg = Message.objects.create(session=session, content=content, content_type=content_type, sender='user')
        session.save()

        ai_text = self._ai_reply(content, content_type)
        ai_msg = Message.objects.create(session=session, content=ai_text, content_type='text', sender='ai')

        return Response({'success': True, 'message': MessageSerializer(user_msg).data, 'ai_message': MessageSerializer(ai_msg).data}, status=status.HTTP_201_CREATED)

    def _ai_reply(self, text: str, content_type: str) -> str:
        try:
            client = TencentDeepSeekClient()
            msgs = [
                {"Role": "system", "Content": get_system_prompt()},
                {"Role": "user", "Content": (text or '') + "\n\n" + get_style_notes()},
            ]
            r = client.chat(msgs, stream=False)
            if r.get('success') and (r.get('text') or '').strip():
                return r['text'].strip()
        except Exception:
            pass
        # fallback
        t = text or ''
        if len(t) <= 8:
            return '我在呢～说说发生了啥，我洗耳恭听！'
        return f"我收到了：{t[:40]}…我们继续聊聊？"


