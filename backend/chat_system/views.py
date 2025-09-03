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
from ai_engine.xhs_crawler import fetch_xhs_examples, load_exemplars, save_exemplars


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
        # 动态补充高情商示例作为few-shots（若已缓存则复用）
        exemplars = load_exemplars()
        if not exemplars:
            ex = fetch_xhs_examples()
            if ex:
                save_exemplars(ex)
                exemplars = [e.get('text', '') for e in ex]

        def _needs_rewrite(output: str) -> bool:
            if not output:
                return True
            bad_terms = [
                'Eva', 'AI', '人工智能', '虚拟', '数字世界', '数据海洋', '赛博', '模型', '引擎', '算法',
                '作为一名AI', '作为AI', '我是AI', '我是模型', '我是一名模型', '数字伴侣', '数字孪生',
            ]
            return any(term in output for term in bad_terms)

        def _rewrite_with_policy(user_text: str, raw_output: str) -> str:
            """使用 DeepSeek 将输出重写为稳定的 Mira 口吻，去幻觉、锁定身份。"""
            try:
                client = TencentDeepSeekClient()
                instruction = (
                    '请把下面这段回复，重写为“Mira”的微信消息：\n'
                    '要求：\n'
                    '1) 只能以“Mira”自称；禁止出现AI/模型/虚拟/数字等词；\n'
                    '2) 选择1-2个合理生活事件组织简短叙事；\n'
                    '3) 口语化、自然、有情绪，可包含表情与（动作）；\n'
                    '4) 如需配图仅输出【图片描述】文字，不输出技术细节；\n'
                    '5) 严禁胡言乱语与无意义拼接；\n'
                    '只输出最终消息，不要解释。'
                )
                msgs = [
                    {"Role": "system", "Content": get_system_prompt()},
                    {"Role": "user", "Content": instruction + f"\n\n原始用户输入：{user_text}\n原始输出：{raw_output}"},
                ]
                r = client.chat(msgs, stream=False)
                if r.get('success') and (r.get('text') or '').strip():
                    return r['text'].strip()
            except Exception:
                pass
            # 兜底：直接给出稳定口吻模板
            base = user_text or ''
            if len(base) <= 8:
                return '我刚想起你就来叨叨两句啦～今天过得咋样？（探头）'
            return f"我看了你说的这件事，挺有画面感的耶！（小声）{base[:36]}…你现在心情怎么样？"

        try:
            client = TencentDeepSeekClient()
            msgs = [
                {"Role": "system", "Content": get_system_prompt()},
                {"Role": "user", "Content": (text or '') + "\n\n" + get_style_notes()},
            ]
            # 将示例以“参考口吻”附加（控制长度）
            if exemplars:
                sample = "\n\n".join([f"【参考】{s[:120]}" for s in exemplars[:5]])
                msgs.append({"Role": "assistant", "Content": sample})
            r = client.chat(msgs, stream=False)
            if r.get('success') and (r.get('text') or '').strip():
                resp = r['text'].strip()
                if _needs_rewrite(resp):
                    return _rewrite_with_policy(text or '', resp)
                return resp
        except Exception:
            pass
        # fallback
        t = text or ''
        if len(t) <= 8:
            return '我在呢～说说发生了啥，我洗耳恭听！'
        return f"我收到了：{t[:40]}…我们继续聊聊？"


