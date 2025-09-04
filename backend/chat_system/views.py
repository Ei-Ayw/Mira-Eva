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
from ai_engine.multimodal_handler import multimodal_handler
from ai_engine.xhs_crawler import fetch_xhs_examples, load_exemplars, save_exemplars
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.cache import cache


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
        client_msg_id = request.data.get('client_msg_id')
        try:
            session = ChatSession.objects.get(id=session_id, user=user, is_active=True)
        except ChatSession.DoesNotExist:
            return Response({'success': False, 'message': '会话不存在或无权限'}, status=status.HTTP_404_NOT_FOUND)

        # 幂等去重：若存在相同 client_msg_id 的用户消息则直接返回，避免重复入库与重复AI回复
        if client_msg_id:
            existed = Message.objects.filter(
                session=session,
                sender='user',
                metadata__client_msg_id=client_msg_id
            ).order_by('-timestamp').first()
            if existed:
                return Response({
                    'success': True,
                    'message': MessageSerializer(existed).data,
                    'ai_message': None,
                    'ai_messages': []
                }, status=status.HTTP_200_OK)

        user_msg = Message.objects.create(
            session=session,
            content=content,
            content_type=content_type,
            sender='user',
            metadata={'client_msg_id': client_msg_id} if client_msg_id else {}
        )
        session.save()

        # 会话状态锁：同一用户/会话同时仅允许一个AI生成任务
        lock_key = f"lock:session:{session.id}"
        got_lock = cache.add(lock_key, '1', timeout=15)
        if not got_lock:
            return Response({
                'success': True,
                'message': MessageSerializer(user_msg).data,
                'ai_message': None,
                'ai_messages': [],
                'status': 'busy'
            }, status=status.HTTP_200_OK)

        # 记录用户最近一次主动消息时间（用于主动触发暂停）
        cache.set(f"last_user_message_at:{user.id}", timezone.now().timestamp(), timeout=3600)

        # 让 LLM 生成单条回复，避免刷屏
        chunks = self._ai_reply_chunks(content, content_type)
        # 若模型建议配图，则将图片生成交给混元
        ai_messages = []
        if not chunks:
            chunks = ["我在呢，继续跟我说说～"]
        text_reply = (chunks or [""])[0]
        # 规则：当文本包含【图片描述】或以“生成一张”开头时，触发图片生成
        wants_image = ('【图片' in text_reply) or text_reply.strip().startswith('生成一张')
        if wants_image:
            # 提取简要描述作为图生图提示
            import re
            desc = re.sub(r"[\[【]图片[^\]】]*[\]】]", "", text_reply)
            desc = (desc or '一张情境照片').strip()
            img = multimodal_handler.generate_image_hunyuan(desc, user_id=user.id)
            if img and img.get('image_url'):
                # 入库图片消息并推送
                ai_img = Message.objects.create(session=session, content=img['image_url'], content_type='image', sender='ai')
                ai_messages.append(ai_img)
                async_to_sync(channel_layer.group_send)(
                    f"chat_{session.id}",
                    {
                        'type': 'chat.message',
                        'message': {
                            'id': ai_img.id,
                            'content': img['image_url'],
                            'sender': 'ai',
                            'content_type': 'image',
                            'timestamp': ai_img.timestamp.isoformat(),
                            'text': desc,
                        }
                    }
                )
        # 仅保留首条文本作为即时广播
        chunks = [text_reply]

        channel_layer = get_channel_layer()
        ai_msgs = []
        for text_part in chunks:
            ai_msg = Message.objects.create(session=session, content=text_part, content_type='text', sender='ai')
            ai_msgs.append(ai_msg)
            payload = {
                'type': 'chat.message',
                'message': {
                    'id': ai_msg.id,
                    'content': text_part,
                    'sender': 'ai',
                    'content_type': 'text',
                    'timestamp': ai_msg.timestamp.isoformat()
                }
            }
            # 仅推送到会话组，避免重复（同一连接通常同时在用户组与会话组）
            async_to_sync(channel_layer.group_send)(f"chat_{session.id}", payload)

        resp_body = {
            'success': True,
            'message': MessageSerializer(user_msg).data,
            'ai_message': MessageSerializer(ai_msgs[0]).data if ai_msgs else None,
            'ai_messages': MessageSerializer(ai_msgs, many=True).data if ai_msgs else []
        }
        # 释放锁
        cache.delete(lock_key)

        return Response(resp_body, status=status.HTTP_201_CREATED)

    def _ai_reply_chunks(self, text: str, content_type: str):
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
            instruction = (
                '你是Mira，请以“碎嘴+口语化”的方式，输出 2-5 句小短句，每句不超过40字。'
                '只输出 JSON，格式：{"sentences": ["句1","句2",...]}。不要额外解释。'
            )
            msgs = [
                {"Role": "system", "Content": get_system_prompt()},
                {"Role": "user", "Content": instruction + "\n\n用户消息：" + (text or '') + "\n\n" + get_style_notes()},
            ]
            if exemplars:
                sample = "\n\n".join([f"【参考】{s[:120]}" for s in exemplars[:5]])
                msgs.append({"Role": "assistant", "Content": sample})
            r = client.chat(msgs, stream=False)
            if r.get('success') and (r.get('text') or '').strip():
                raw = r['text'].strip()
                import json
                try:
                    data = json.loads(raw)
                    arr = data.get('sentences') if isinstance(data, dict) else None
                    chunks = [s.strip() for s in (arr or []) if isinstance(s, str) and s.strip()]
                    if 1 <= len(chunks) <= 5:
                        return self._post_process_chunks(chunks)
                except Exception:
                    pass
                # 若非JSON，回退为重写后单句拆分
                candidate = _rewrite_with_policy(text or '', raw)
                return self._post_process_chunks(self._split_short_sentences(candidate))
        except Exception:
            pass
        # fallback：按用户句子生成友好回应并拆分
        candidate = _rewrite_with_policy(text or '', (text or ''))
        return self._post_process_chunks(self._split_short_sentences(candidate))

    def _split_short_sentences(self, text: str):
        """将一段文本按句号/换行拆成<=5条短句"""
        if not text:
            return ["我在呢～继续跟我说说？"]
        import re
        parts = re.split(r"[\n。！？!?]+", text)
        cleaned = [p.strip() for p in parts if p.strip()]
        if not cleaned:
            return [text]
        return cleaned[:5]

    def _post_process_chunks(self, chunks):
        """对短句做安全与风格规整：去文件名/长括号、限长、去重、补标点。"""
        import re
        seen = set()
        out = []
        for raw in chunks:
            s = (raw or '').strip()
            if not s:
                continue
            # 去除文件名/链接
            s = re.sub(r"\S+\.(?:jpg|jpeg|png|gif|webp)\b", "", s, flags=re.IGNORECASE)
            s = re.sub(r"https?://\S+", "", s)
            # 收敛括号内容过长
            s = re.sub(r"（[^）]{15,}）", "（…）", s)
            s = re.sub(r"\([^)]{15,}\)", "（…）", s)
            # 压缩空白
            s = re.sub(r"\s+", " ", s)
            # 限长：保持 10~28 字左右
            max_len = 28
            if len(s) > max_len:
                s = s[:max_len].rstrip()
            # 末尾补标点
            if not re.search(r"[。！？!]$", s):
                s = s + "。"
            # 去重（忽略标点）
            key = re.sub(r"[。！？!,.，\s]", "", s)
            if key in seen:
                continue
            seen.add(key)
            out.append(s)
            if len(out) >= 5:
                break
        # 至少两句，若不足，用温柔收尾
        if len(out) == 1:
            out.append("我在呢，慢慢说就好～")
        return out or ["我在呢～继续跟我说说？"]


