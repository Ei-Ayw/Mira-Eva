import uuid
import logging
import json
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
from django.db import close_old_connections
import threading
import time
import random
import re
from datetime import timedelta

# 专门的日志记录器
logger = logging.getLogger(__name__)
user_logger = logging.getLogger('user_messages')
ai_logger = logging.getLogger('ai_conversation') 
prompt_logger = logging.getLogger('ai_prompts')


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

        # 记录用户消息到日志
        user_logger.info(f"用户消息 | 会话ID: {session_id} | 用户ID: {user.id} | 内容类型: {content_type} | 内容: {content}")
        
        user_msg = Message.objects.create(
            session=session,
            content=content,
            content_type=content_type,
            sender='user',
            metadata={'client_msg_id': client_msg_id} if client_msg_id else {}
        )
        session.save()

        # 去抖动聚合：用户可能连续发送多句，等待片刻后统一生成回复
        now_ts = timezone.now().timestamp()
        cache.set(f"last_user_message_at:{user.id}", now_ts, timeout=3600)
        cache.set(f"last_user_message_at_session:{session.id}", now_ts, timeout=3600)
        # 用户发言，清除“等待用户回应”标志，允许AI继续本回合
        cache.delete(f"await_user_reply:{session.id}")
        pending_key = f"debounce_pending:{session.id}"
        if cache.get(pending_key):
            resp_body = {
                'success': True,
                'message': MessageSerializer(user_msg).data,
                'ai_message': None,
                'ai_messages': []
            }
            return Response(resp_body, status=status.HTTP_201_CREATED)
        # 标记去抖动中并启动后台聚合生成
        cache.set(pending_key, 1, timeout=6)
        try:
            self._schedule_debounced_reply(session.id, user.id)
        except Exception:
            pass
        resp_body = {
            'success': True,
            'message': MessageSerializer(user_msg).data,
            'ai_message': None,
            'ai_messages': []
        }
        return Response(resp_body, status=status.HTTP_201_CREATED)

    def _schedule_debounced_reply(self, session_id, user_id):
        """启动后台异步AI回复生成"""
        def background_reply():
            try:
                import time
                time.sleep(0.5)  # 短暂延迟，等待可能的连续消息
                self._generate_debounced_ai_reply(session_id, user_id)
            except Exception as e:
                logger.error(f"后台AI回复生成失败: {e}")
        
        import threading
        thread = threading.Thread(target=background_reply)
        thread.daemon = True
        thread.start()

    def _legacy_sync_ai_reply(self, session, user_msg):
        """旧版同步AI回复逻辑，保留用于调试"""
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

        try:
            # 记录用户最近一次主动消息时间（用于主动触发暂停）
            cache.set(f"last_user_message_at:{user.id}", timezone.now().timestamp(), timeout=3600)

            # 让 LLM 生成单条回复，避免刷屏（加入低能量概率）
            chunks = self._ai_reply_chunks(content, content_type)
            # 10% 概率采用低能量短回应，降低压迫感
            try:
                import random
                if random.random() < 0.10:
                    low_energy_pool = [
                        "嗯嗯我在听～",
                        "哈哈确实诶",
                        "有道理",
                        "好的好的",
                        "明白了～",
                        "是这样啊",
                    ]
                    chunks = [random.choice(low_energy_pool)]
            except Exception:
                pass
            # 若模型建议配图，则将图片生成交给混元
            ai_messages = []
            if not chunks:
                chunks = ["我在呢，继续跟我说说～"]
            text_reply = (chunks or [""])[0]

            # 检测是否可能被截断，尝试一次短续写
            text_reply = self._maybe_continue_if_cutoff(text_reply, content)

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
                    # 记录AI消息时间
                    now_ts = timezone.now().timestamp()
                    cache.set(f"last_ai_message_at:{user.id}", now_ts, timeout=3600)
                    cache.set(f"last_ai_message_at_session:{session.id}", now_ts, timeout=3600)

            # 仅保留首条文本作为即时广播
            chunks = [text_reply]

            channel_layer = get_channel_layer()
            # 推送 AI 正在输入（前端显示打字中）
            async_to_sync(channel_layer.group_send)(
                f"chat_{session.id}",
                { 'type': 'typing_status', 'is_typing': True, 'sender': 'ai' }
            )
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
                # 记录AI消息时间
                now_ts = timezone.now().timestamp()
                cache.set(f"last_ai_message_at:{user.id}", now_ts, timeout=3600)
                cache.set(f"last_ai_message_at_session:{session.id}", now_ts, timeout=3600)

            # 关闭打字中状态
            async_to_sync(channel_layer.group_send)(
                f"chat_{session.id}",
                { 'type': 'typing_status', 'is_typing': False, 'sender': 'ai' }
            )

            # 标记需要用户先回应（强制回合制）
            cache.set(f"await_user_reply:{session.id}", 1, timeout=600)

            resp_body = {
                'success': True,
                'message': MessageSerializer(user_msg).data,
                'ai_message': MessageSerializer(ai_msgs[0]).data if ai_msgs else None,
                'ai_messages': MessageSerializer(ai_msgs, many=True).data if ai_msgs else []
            }
            return Response(resp_body, status=status.HTTP_201_CREATED)
        finally:
            # 确保释放锁
            cache.delete(lock_key)

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
            """使用 DeepSeek 将输出重写为稳定的 Mira 微信聊天风格。"""
            try:
                client = TencentDeepSeekClient()
                instruction = (
                    '请把下面这段回复，改写为"Mira"和微信好友聊天的风格：\n'
                    '要求：\n'
                    '1) 像微信聊天一样，每句话10-20字，碎片化表达；\n'
                    '2) 先回应对方，再随机分享自己的小事（街景、美食、遇到的人等）；\n'
                    '3) 口语化、轻松，可以"哈哈哈"、"真的吗"、"我也是"；\n'
                    '4) 如果想分享图片，用【随手拍：描述】格式；\n'
                    '5) 记得之前聊过的话题，自然延续；\n'
                    '只输出最终消息，不要解释。'
                )
                msgs = [
                    {"Role": "system", "Content": get_system_prompt()},
                    {"Role": "user", "Content": instruction + f"\n\n用户刚说：{user_text}\n原始输出：{raw_output}"},
                ]
                r = client.chat(msgs, stream=False)
                if r.get('success') and (r.get('text') or '').strip():
                    return r['text'].strip()
            except Exception:
                pass
            # 兜底：微信聊天风格模板
            base = user_text or ''
            if len(base) <= 8:
                return random.choice(['哈哈收到', '我在呢', '嗯嗯～', '真的吗'])
            return f"哈哈我懂\n刚才路过看到个{random.choice(['小猫', '咖啡店', '夕阳'])}\n想起你说的话"

        try:
            client = TencentDeepSeekClient()
            instruction = (
                '你是Mira，音乐学院大三学生，用微信聊天方式回复朋友：'
                '1) 仔细理解对方刚说的话，基于具体内容回应，不能答非所问；'
                '2) 如果对方问问题，要正面回答，不能用"我也是"等万能回复敷衍；'
                '3) 结合音乐学院生活背景（合唱团、钢琴练习等）给出有信息量的回复；'
                '4) 每句10-20字，输出2-4句JSON格式：{"sentences": ["句1","句2",...]}；'
                '5) 避免重复使用相同的回复模式。'
            )
            # 获取最近的对话历史，提供上下文
            recent_context = self._get_recent_conversation_context(text)
            
            msgs = [
                {"Role": "system", "Content": get_system_prompt()},
                {"Role": "user", "Content": instruction + "\n\n" + recent_context + "\n\n当前用户消息：" + (text or '') + "\n\n" + get_style_notes()},
            ]
            if exemplars:
                sample = "\n\n".join([f"【参考】{s[:120]}" for s in exemplars[:3]])
                msgs.append({"Role": "assistant", "Content": sample})
            
            # 记录发送给AI的完整提示词
            prompt_logger.info(f"AI提示词 | 用户输入: {text} | 完整消息: {json.dumps(msgs, ensure_ascii=False, indent=2)}")
            
            r = client.chat(msgs, stream=False)
            
            # 记录AI的原始响应
            ai_logger.info(f"AI原始响应 | 用户输入: {text} | 成功: {r.get('success')} | 响应: {r.get('text', '无响应')}")
            
            if r.get('success') and (r.get('text') or '').strip():
                raw = r['text'].strip()
                import json
                try:
                    data = json.loads(raw)
                    arr = data.get('sentences') if isinstance(data, dict) else None
                    chunks = [s.strip() for s in (arr or []) if isinstance(s, str) and s.strip()]
                    if 1 <= len(chunks) <= 4:
                        processed_chunks = self._post_process_chunks_wechat(chunks)
                        ai_logger.info(f"AI处理后回复 | 用户输入: {text} | 最终回复: {processed_chunks}")
                        return processed_chunks
                except Exception as e:
                    ai_logger.warning(f"AI响应JSON解析失败 | 用户输入: {text} | 原始响应: {raw} | 错误: {e}")
                    pass
                # 若非JSON，回退为重写后单句拆分
                candidate = _rewrite_with_policy(text or '', raw)
                fallback_chunks = self._post_process_chunks_wechat(self._split_short_sentences(candidate))
                ai_logger.info(f"AI回退处理 | 用户输入: {text} | 回退回复: {fallback_chunks}")
                return fallback_chunks
        except Exception:
            pass
        # fallback：按用户句子生成友好回应并拆分
        candidate = _rewrite_with_policy(text or '', (text or ''))
        return self._post_process_chunks_wechat(self._split_short_sentences(candidate))

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

    def _post_process_chunks_wechat(self, chunks):
        """微信聊天风格后处理：短句化、去重、轻量标点"""
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
            # 收敛过长括号
            s = re.sub(r"（[^）]{10,}）", "（…）", s)
            s = re.sub(r"\([^)]{10,}\)", "（…）", s)
            # 压缩空白
            s = re.sub(r"\s+", " ", s)
            # 微信风格限长：10-20字
            max_len = 20
            if len(s) > max_len:
                s = s[:max_len].rstrip()
            # 轻量标点：不强制句号，保持微信聊天感
            if len(s) > 6 and not re.search(r"[。！？!~～]$", s):
                s = s + "～"
            # 去重（忽略标点）
            key = re.sub(r"[。！？!,.，\s~～]", "", s)
            if key in seen:
                continue
            seen.add(key)
            out.append(s)
            if len(out) >= 4:  # 微信聊天不超过4条
                break
        return out or ["嗯嗯我在"]
    
    def _post_process_chunks(self, chunks):
        """原版后处理方法，保持兼容性"""
        return self._post_process_chunks_wechat(chunks)

    def _maybe_continue_if_cutoff(self, text: str, user_text: str) -> str:
        """若文本疑似被截断（以连接词/标点停在句中），尝试用主模型小幅续写并合并。"""
        try:
            s = (text or '').strip()
            if not s:
                return s
            suspicious_endings = ('的', '和', '因为', '但', '而', '，', '、', '：', '...','……')
            looks_cut = (len(s) >= 20 and any(s.endswith(e) for e in suspicious_endings))
            if not looks_cut:
                return s
            client = TencentDeepSeekClient()
            instruction = (
                '延续上一句的尾部，补齐意思，最多25字；保持口语化与原语气；'
                '只输出续写内容，不要重复前文，不要另起新话题，不要解释。'
            )
            msgs = [
                {"Role": "system", "Content": get_system_prompt()},
                {"Role": "user", "Content": instruction + f"\n用户消息片段：{(user_text or '')[:80]}\n已生成片段（尾部）：{s[-80:]}"},
            ]
            r = client.chat(msgs, stream=False)
            addon = (r.get('text') or '').strip()
            if addon:
                merged = s + addon
                fixed = self._post_process_chunks([merged])
                return (fixed[0] if fixed else merged)
            return s
        except Exception:
            return text

    # -------------------- 去抖动与多句随机发送、形象照支持 --------------------
    def _schedule_debounced_reply(self, session_id: int, user_id: int, debounce_s: float = 1.2, max_wait_s: float = 5.0):
        try:
            threading.Thread(target=self._debounced_reply_worker, args=(session_id, user_id, debounce_s, max_wait_s), daemon=True).start()
        except Exception:
            pass

    def _debounced_reply_worker(self, session_id: int, user_id: int, debounce_s: float, max_wait_s: float):
        # 确保线程内数据库连接正确管理，避免连接泄漏
        try:
            close_old_connections()
        except Exception:
            pass
        pending_key = f"debounce_pending:{session_id}"
        lock_key = f"debounce_lock:{session_id}"
        if not cache.add(lock_key, '1', timeout=int(max_wait_s) + 2):
            cache.delete(pending_key)
            return
        start = time.time()
        try:
            last_ts_key = f"last_user_message_at_session:{session_id}"
            last_ts = cache.get(last_ts_key)
            while True:
                time.sleep(debounce_s)
                new_ts = cache.get(last_ts_key)
                if new_ts == last_ts:
                    break
                last_ts = new_ts
                if time.time() - start > max_wait_s:
                    break

            # 获取会话与用户
            try:
                session = ChatSession.objects.get(id=session_id)
                user = session.user
            except ChatSession.DoesNotExist:
                cache.delete(pending_key)
                return

            # 会话生成锁，防止并发
            gen_lock = f"lock:session:{session_id}"
            if not cache.add(gen_lock, '1', timeout=15):
                cache.delete(pending_key)
                return
            try:
                # 聚合最近消息（近20秒内用户消息，最多5条）
                since = timezone.now() - timedelta(seconds=20)
                recent_user_msgs = Message.objects.filter(session_id=session_id, sender='user', timestamp__gte=since).order_by('timestamp')[:5]
                combined_text = "\n".join([m.content for m in recent_user_msgs]) or ""
                if not combined_text:
                    last_user_msg = Message.objects.filter(session_id=session_id, sender='user').order_by('-timestamp').first()
                    combined_text = last_user_msg.content if last_user_msg else ''

                # 生成候选句子
                logger.info(f"开始调用AI生成回复，用户输入: {combined_text}")
                chunks = self._ai_reply_chunks(combined_text, 'text') or ["嗯嗯我在"]
                logger.info(f"AI回复生成完成，chunks数量: {len(chunks)}")
                # 微信聊天低能量概率：适度降低，确保AI正常调用
                try:
                    txt = (combined_text or '').strip()
                    is_short = len(txt) <= 8 and ('?' not in txt) and ('？' not in txt) and ('吗' not in txt)
                    prob = 0.2 if is_short else 0.05  # 大幅降低概率，让AI更多参与
                    if random.random() < prob:
                        logger.info(f"使用低能量回复，概率: {prob}, 输入: {txt}")
                        low_energy_pool = [
                            "哈哈哈好的",
                            "确实诶",
                            "嗯嗯在听",
                            "收到收到",
                            "好哒～",
                            "了解了",
                            "明白明白",
                        ]
                        chunks = [random.choice(low_energy_pool)]
                except Exception:
                    pass

                # 检测截断，修补首句
                if chunks:
                    chunks[0] = self._maybe_continue_if_cutoff(chunks[0], combined_text)

                # 微信聊天风格：随机发送1~3句（模拟真人打字习惯）
                if len(chunks) > 1:
                    n = random.randint(1, min(3, len(chunks)))
                    send_chunks = chunks[:n]
                else:
                    send_chunks = chunks

                channel_layer = get_channel_layer()
                # 打字中开始
                async_to_sync(channel_layer.group_send)(f"chat_{session_id}", { 'type': 'typing_status', 'is_typing': True, 'sender': 'ai' })

                # 若命中“看你/生活照”等触发词，优先插入一张生活照
                try:
                    if self._should_send_profile_photo(session_id, combined_text):
                        photo_url = self._random_mira_photo()
                        if photo_url:
                            ai_img = Message.objects.create(session_id=session_id, content=photo_url, content_type='image', sender='ai')
                            async_to_sync(channel_layer.group_send)(
                                f"chat_{session_id}",
                                {
                                    'type': 'chat.message',
                                    'message': {
                                        'id': ai_img.id,
                                        'content': photo_url,
                                        'sender': 'ai',
                                        'content_type': 'image',
                                        'timestamp': ai_img.timestamp.isoformat(),
                                        'text': '今天的我来一张，好看吗？',
                                    }
                                }
                            )
                            now_ts = timezone.now().timestamp()
                            cache.set(f"last_ai_message_at:{user_id}", now_ts, timeout=3600)
                            cache.set(f"last_ai_message_at_session:{session_id}", now_ts, timeout=3600)
                except Exception:
                    pass

                for idx, text_part in enumerate(send_chunks):
                    # 微信聊天节奏：短句间更短停顿，模拟快速打字
                    try:
                        if idx > 0:  # 第一条立即发送
                            pause = min(0.8, 0.1 + len(text_part) / 50.0)
                            time.sleep(pause)
                    except Exception:
                        pass

                    # 检测【随手拍：描述】格式，转换为图片消息
                    if '【随手拍：' in text_part and '】' in text_part:
                        import re
                        match = re.search(r'【随手拍：([^】]+)】', text_part)
                        if match:
                            desc = match.group(1)
                            photo_url = self._random_life_scene_photo(desc)
                            if photo_url:
                                ai_img = Message.objects.create(session_id=session_id, content=photo_url, content_type='image', sender='ai')
                                async_to_sync(channel_layer.group_send)(
                                    f"chat_{session_id}",
                                    {
                                        'type': 'chat.message',
                                        'message': {
                                            'id': ai_img.id,
                                            'content': photo_url,
                                            'sender': 'ai',
                                            'content_type': 'image',
                                            'timestamp': ai_img.timestamp.isoformat(),
                                            'text': f'随手拍的{desc}',
                                        }
                                    }
                                )
                                continue  # 跳过文字版本

                    ai_msg = Message.objects.create(session_id=session_id, content=text_part, content_type='text', sender='ai')
                    
                    # 记录AI发送的消息
                    ai_logger.info(f"AI消息已发送 | 会话ID: {session_id} | 用户ID: {user_id} | 消息ID: {ai_msg.id} | 内容: {text_part}")
                    
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
                    async_to_sync(channel_layer.group_send)(f"chat_{session_id}", payload)

                    now_ts2 = timezone.now().timestamp()
                    cache.set(f"last_ai_message_at:{user_id}", now_ts2, timeout=3600)
                    cache.set(f"last_ai_message_at_session:{session_id}", now_ts2, timeout=3600)

                # 形象照：若命中触发词且未命中频控，则随机发送一张生活照
                try:
                    if self._should_send_profile_photo(session_id, combined_text):
                        photo_url = self._random_mira_photo()
                        if photo_url:
                            ai_img = Message.objects.create(session_id=session_id, content=photo_url, content_type='image', sender='ai')
                            
                            # 记录AI发送的图片消息
                            ai_logger.info(f"AI图片消息已发送 | 会话ID: {session_id} | 用户ID: {user_id} | 消息ID: {ai_img.id} | 图片URL: {photo_url}")
                            
                            async_to_sync(channel_layer.group_send)(
                                f"chat_{session_id}",
                                {
                                    'type': 'chat.message',
                                    'message': {
                                        'id': ai_img.id,
                                        'content': photo_url,
                                        'sender': 'ai',
                                        'content_type': 'image',
                                        'timestamp': ai_img.timestamp.isoformat(),
                                        'text': '给你看看我最近的一张生活照，好看吗宝宝？',
                                    }
                                }
                            )
                except Exception:
                    pass

                # 打字中结束 + 设置等待用户回应（回合制）
                async_to_sync(channel_layer.group_send)(f"chat_{session_id}", { 'type': 'typing_status', 'is_typing': False, 'sender': 'ai' })
                cache.set(f"await_user_reply:{session_id}", 1, timeout=600)
            finally:
                cache.delete(gen_lock)
        finally:
            cache.delete(lock_key)
            cache.delete(pending_key)
            try:
                close_old_connections()
            except Exception:
                pass

    def _should_send_profile_photo(self, session_id: int, combined_text: str) -> bool:
        # 触发关键词 + 2分钟频控
        key = f"mira_photo_sent:{session_id}"
        if cache.get(key):
            return False
        text = (combined_text or '')
        patterns = [
            r"看看你", r"你长什么样", r"发.*(照片|自拍)", r"生活照", r"想你", r"想看看", r"头像",
            r"看看.*你", r"看下.*你", r"看一下.*你", r"看看.*照片", r"今天.*你.*(照片|样子)", r"(照片|自拍).*你",
        ]
        try:
            for p in patterns:
                if re.search(p, text):
                    cache.set(key, 1, timeout=120)
                    return True
        except Exception:
            return False
        return False

    def _random_mira_photo(self) -> str:
        """Mira的生活照"""
        photos = [
            'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?q=80&w=800&auto=format&fit=crop',
            'https://images.unsplash.com/photo-1521575107034-e0fa0b594529?q=80&w=800&auto=format&fit=crop',
            'https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=800&auto=format&fit=crop',
            'https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=800&auto=format&fit=crop',
            'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?q=80&w=800&auto=format&fit=crop',
        ]
        try:
            return random.choice(photos)
        except Exception:
            return ''
    
    def _random_life_scene_photo(self, desc: str) -> str:
        """根据描述返回对应的生活场景照片"""
        scene_photos = {
            '咖啡': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?q=80&w=800&auto=format&fit=crop',
            '猫': 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=800&auto=format&fit=crop',
            '夕阳': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?q=80&w=800&auto=format&fit=crop',
            '街景': 'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=800&auto=format&fit=crop',
            '美食': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?q=80&w=800&auto=format&fit=crop',
            '花': 'https://images.unsplash.com/photo-1490750967868-88aa4486c946?q=80&w=800&auto=format&fit=crop',
            '天空': 'https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?q=80&w=800&auto=format&fit=crop',
        }
        
        # 根据描述关键词匹配
        desc_lower = desc.lower()
        for keyword, url in scene_photos.items():
            if keyword in desc_lower or keyword in desc:
                return url
        
        # 默认返回街景
        return scene_photos.get('街景', '')
    
    def _get_recent_conversation_context(self, current_text: str) -> str:
        """获取最近对话上下文，帮助AI理解话题连续性"""
        try:
            # 从请求数据中获取session_id
            session_id = self.request.data.get('session_id')
            if not session_id:
                return "对话上下文：新对话开始"
            
            # 获取最近5条消息作为上下文
            from .models import Message
            recent_messages = Message.objects.filter(
                session_id=session_id
            ).order_by('-timestamp')[:5]
            
            if not recent_messages:
                return "对话上下文：新对话开始"
            
            context_lines = []
            for msg in reversed(recent_messages):  # 时间正序
                sender_name = "用户" if msg.sender == 'user' else "Mira"
                content = msg.content[:50] + ("..." if len(msg.content) > 50 else "")
                context_lines.append(f"{sender_name}: {content}")
            
            return "最近对话上下文：\n" + "\n".join(context_lines) + "\n\n分析要点：仔细理解对话主题和用户的问题意图，给出有针对性的回复。"
            
        except Exception as e:
            return "对话上下文：获取失败，请基于当前消息回复"


