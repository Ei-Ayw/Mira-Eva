import asyncio
import logging
from datetime import datetime, timedelta
import random
from django.utils import timezone
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ai_engine.tencent_client import TencentDeepSeekClient
from ai_engine.prompt_library import get_proactive_prompt
from ai_engine.emotion_analyzer import emotion_analyzer
import time
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ProactiveEngine:
    """主动触发引擎 - Mira的核心创新功能"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.connected_users = set()  # 存储在线用户ID
        self.user_sessions = {}  # 存储用户会话信息
        self.last_connect_greet_at = {}  # 记录连接后问候的时间
        
    def should_trigger_greeting(self, user_id, last_interaction):
        """判断是否应该发送问候"""
        if not last_interaction:
            return True
            
        # 如果超过12小时没有互动，发送问候
        time_diff = timezone.now() - last_interaction
        return time_diff > timedelta(hours=12)
    
    def should_trigger_care(self, user_id, recent_messages):
        """基于最近对话内容判断是否需要关怀"""
        if not recent_messages:
            return False
            
        # 获取最近5条用户消息
        recent_user_messages = [msg for msg in recent_messages[-5:] if msg.get('sender') == 'user']
        if not recent_user_messages:
            return False
        
        # 合并最近消息文本
        recent_text = ' '.join([msg.get('content', '') for msg in recent_user_messages])
        
        # 使用情绪分析器分析
        emotion_analysis = emotion_analyzer.analyze_text_emotion(recent_text)
        
        # 判断是否需要关怀
        should_care = emotion_analyzer.should_trigger_care(emotion_analysis)
        
        logger.info(f"用户 {user_id} 情绪分析: {emotion_analysis['primary_emotion']}, 需要关怀: {should_care}")
        
        return should_care
    
    def should_trigger_share(self, user_id, last_share):
        """判断是否应该主动分享生活"""
        if not last_share:
            return True
            
        # 如果超过6小时没有主动分享，发起话题
        time_diff = timezone.now() - last_share
        return time_diff > timedelta(hours=6)
    
    def generate_proactive_message(self, trigger_type, user_context=None):
        """生成主动消息"""
        try:
            # 获取主动触发提示词
            prompt = get_proactive_prompt(trigger_type, user_context)
            
            # 调用AI生成回复
            client = TencentDeepSeekClient()
            messages = [{"Role": "user", "Content": prompt}]
            result = client.chat(messages)
            response = result.get('text', '') if result.get('success') else ''
            
            logger.info(f"主动触发消息生成成功: {trigger_type}")
            return response
            
        except Exception as e:
            logger.error(f"主动触发消息生成失败: {e}")
            # 返回默认消息
            return self.get_default_message(trigger_type)
    
    def get_default_message(self, trigger_type):
        """获取默认的主动消息"""
        default_messages = {
            'greeting': "嗨！今天过得怎么样？我刚刚看到窗外的阳光特别好，想和你分享一下～",
            'care': "感觉你最近有点累呢，要不要聊聊？我随时都在这里陪着你。",
            'share': "诶，我突然想到一个有趣的事情想和你分享！你猜我今天遇到了什么？",
            'reminder': "我们好像好久没聊天了，想你了！最近有什么新鲜事吗？"
        }
        return default_messages.get(trigger_type, "嗨！想和你聊聊天～")
    
    def add_connected_user(self, user_id, session_id=None):
        """添加在线用户"""
        self.connected_users.add(user_id)
        if session_id:
            self.user_sessions[user_id] = session_id
        logger.info(f"用户 {user_id} 已连接，当前在线用户: {len(self.connected_users)}")
    
    def remove_connected_user(self, user_id):
        """移除离线用户"""
        self.connected_users.discard(user_id)
        self.user_sessions.pop(user_id, None)
        logger.info(f"用户 {user_id} 已断开，当前在线用户: {len(self.connected_users)}")
    
    def is_user_online(self, user_id):
        """检查用户是否在线"""
        return user_id in self.connected_users
    
    def get_online_users(self):
        """获取所有在线用户"""
        return list(self.connected_users)
    
    def send_proactive_message(self, user_id, message, message_type="proactive"):
        """发送主动消息到指定用户"""
        try:
            # 在用户主动发言后60秒内暂停主动触发
            last_ts = cache.get(f"last_user_message_at:{user_id}")
            if last_ts:
                delta = timezone.now().timestamp() - float(last_ts)
                if delta < 60:
                    logger.info(f"用户 {user_id} 最近{int(delta)}秒内有发言，跳过主动触发")
                    return False

            # 最近10分钟内若AI刚说过话，且会话内最后一条消息是AI，则不要插话，等待用户先说
            last_ai_ts = cache.get(f"last_ai_message_at:{user_id}")
            if last_ai_ts:
                if timezone.now().timestamp() - float(last_ai_ts) < 600:
                    try:
                        from chat_system.models import ChatSession, Message
                        session_id = self.user_sessions.get(user_id)
                        if session_id:
                            if str(session_id).isdigit():
                                session = ChatSession.objects.get(id=int(session_id))
                            else:
                                session = ChatSession.objects.get(session_id=str(session_id))
                            last_msg = Message.objects.filter(session=session).order_by('-timestamp').first()
                            if last_msg and last_msg.sender == 'ai':
                                logger.info("上条为AI消息，等待用户先说，跳过主动触发")
                                return False
                    except Exception:
                        pass
            # 检查用户是否在线
            if not self.is_user_online(user_id):
                logger.warning(f"用户 {user_id} 不在线，跳过主动消息发送")
                return False
            
            payload = {
                "type": "chat.message",
                "message": {
                    "content": message,
                    "sender": "ai",
                    "content_type": "text",
                    "message_type": message_type,
                    "timestamp": timezone.now().isoformat(),
                    "is_proactive": True
                }
            }

            # 若会话处于等待用户回应阶段（回合制），则不主动打断
            session_id = self.user_sessions.get(user_id)
            if session_id:
                await_key = f"await_user_reply:{session_id}"
                if cache.get(await_key):
                    logger.info(f"会话 {session_id} 正在等待用户回应，跳过主动触发")
                    return False

            # 仅发送到优先的会话组；若没有已知会话，退回到用户组
            if session_id:
                async_to_sync(self.channel_layer.group_send)(f"chat_{session_id}", payload)
            else:
                async_to_sync(self.channel_layer.group_send)(f"chat_{user_id}", payload)
            
            logger.info(f"主动消息发送成功: user_id={user_id}, type={message_type}")
            return True
            
        except Exception as e:
            logger.error(f"主动消息发送失败: {e}")
            return False
    
    def send_proactive_message_to_all_online(self, message, message_type="proactive"):
        """向所有在线用户发送主动消息"""
        sent_count = 0
        for user_id in self.connected_users:
            if self.send_proactive_message(user_id, message, message_type):
                sent_count += 1
        
        logger.info(f"向 {sent_count} 个在线用户发送了主动消息")
        return sent_count

    def _get_user_recent_messages(self, user, within_seconds: int = 10):
        """获取用户在最近within_seconds秒内与AI的任何消息（用户或AI）"""
        from chat_system.models import ChatSession, Message
        since = timezone.now() - timedelta(seconds=within_seconds)
        sessions = ChatSession.objects.filter(user=user, is_active=True)
        return Message.objects.filter(
            session__in=sessions,
            timestamp__gte=since
        ).order_by('-timestamp')

    def should_send_silent_prompt(self, user) -> bool:
        """最近10秒无用户或AI消息，则返回True"""
        recent = self._get_user_recent_messages(user, within_seconds=10)
        return not recent.exists()

    def send_welcome_on_connect(self, user_id: int, cooldown_minutes: int = 5):
        """用户建立连接后发送一次问候（带冷却）"""
        try:
            last_at = self.last_connect_greet_at.get(user_id)
            if last_at and timezone.now() - last_at < timedelta(minutes=cooldown_minutes):
                return False

            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
            # 若最近10秒内已有对话（用户或AI），则跳过此次问候，避免打断
            if not self.should_send_silent_prompt(user):
                return False
            greeting_message = self.generate_proactive_message('greeting', {
                'user_name': user.username,
                'time_of_day': self.get_time_greeting()
            })
            sent = self.send_proactive_message(user_id, greeting_message, 'greeting')
            if sent:
                self.last_connect_greet_at[user_id] = timezone.now()
            return sent
        except Exception as e:
            logger.error(f"连接问候发送失败: {e}")
            return False
    
    def process_user_activity(self, user_id, activity_type, content=None):
        """处理用户活动，决定是否触发主动关怀"""
        try:
            from chat_system.models import UserActivity, ConversationHistory
            
            # 记录用户活动
            UserActivity.objects.create(
                user_id=user_id,
                activity_type=activity_type,
                content=content,
                timestamp=timezone.now()
            )
            
            # 获取用户最近活动
            recent_activities = UserActivity.objects.filter(
                user_id=user_id
            ).order_by('-timestamp')[:10]
            
            # 分析是否需要主动关怀
            if self.should_trigger_care(user_id, recent_activities):
                care_message = self.generate_proactive_message('care', {
                    'recent_activities': recent_activities
                })
                self.send_proactive_message(user_id, care_message, 'care')
                
        except Exception as e:
            logger.error(f"处理用户活动失败: {e}")
    
    def run_daily_tasks(self):
        """保留的低频任务（可扩展），当前不做重度逻辑"""
        try:
            pass
        except Exception as e:
            logger.error(f"运行每日任务失败: {e}")

    def run_periodic_tasks(self):
        """高频周期任务：每1~2分钟检测静默并发送关怀/分享"""
        try:
            from django.contrib.auth.models import User
            online_users = self.get_online_users()
            if not online_users:
                logger.info("没有在线用户，跳过周期任务")
                return

            for user_id in online_users:
                try:
                    user = User.objects.get(id=user_id)
                    # 10秒内无任何消息 -> 触发
                    if self.should_send_silent_prompt(user):
                        # 随机选择更自然的消息类型
                        trigger_type = random.choice(['share', 'greeting', 'care'])
                        message = self.generate_proactive_message(trigger_type, {
                            'user_name': user.username,
                            'time_of_day': self.get_time_greeting()
                        })
                        self.send_proactive_message(user.id, message, trigger_type)
                except User.DoesNotExist:
                    self.remove_connected_user(user_id)
                except Exception as e:
                    logger.error(f"周期任务处理用户 {user_id} 异常: {e}")
        except Exception as e:
            logger.error(f"运行周期任务失败: {e}")
    
    def send_message_to_user(self, user_id, message, message_type="proactive"):
        """直接向指定用户发送消息"""
        try:
            if not self.is_user_online(user_id):
                logger.warning(f"用户 {user_id} 不在线，无法发送消息")
                return False
            
            return self.send_proactive_message(user_id, message, message_type)
        except Exception as e:
            logger.error(f"向用户 {user_id} 发送消息失败: {e}")
            return False
    
    def get_time_greeting(self):
        """根据时间返回合适的问候语"""
        hour = timezone.now().hour
        
        if 5 <= hour < 12:
            return "早上好"
        elif 12 <= hour < 18:
            return "下午好"
        elif 18 <= hour < 22:
            return "晚上好"
        else:
            return "夜深了"
    
    def start_background_tasks(self):
        """启动后台任务"""
        try:
            logger.info("主动触发引擎后台服务启动中...")

            # 启动时跑一次低频任务
            self.run_daily_tasks()

            # 高频周期：每1~2分钟带抖动执行一次静默检测
            while True:
                try:
                    # 随机等待 60~120 秒，避免同质化
                    wait_s = random.randint(60, 120)
                    time.sleep(wait_s)
                    logger.info(f"执行主动触发引擎周期任务（间隔 {wait_s}s）...")
                    self.run_periodic_tasks()
                except KeyboardInterrupt:
                    logger.info("主动触发引擎收到停止信号")
                    break
                except Exception as e:
                    logger.error(f"定时任务执行失败: {e}")
                    # 继续运行，不因单次失败而停止
                    continue
                
        except Exception as e:
            logger.error(f"后台任务运行失败: {e}")

# 全局实例
proactive_engine = ProactiveEngine()

def start_proactive_engine():
    """启动主动触发引擎"""
    try:
        logger.info("启动主动触发引擎...")
        proactive_engine.start_background_tasks()
    except Exception as e:
        logger.error(f"启动主动触发引擎失败: {e}")

if __name__ == "__main__":
    # 测试主动触发引擎
    engine = ProactiveEngine()
    
    # 测试消息生成
    test_message = engine.generate_proactive_message('greeting', {
        'user_name': '测试用户',
        'time_of_day': '早上好'
    })
    print(f"测试消息: {test_message}")
    
    # 测试默认消息
    default_message = engine.get_default_message('care')
    print(f"默认消息: {default_message}")
