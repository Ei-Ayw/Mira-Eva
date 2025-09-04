from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from chat_system.proactive import proactive_engine
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '查看当前在线用户'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--send-test',
            type=str,
            help='向所有在线用户发送测试消息'
        )
    
    def handle(self, *args, **options):
        try:
            online_users = proactive_engine.get_online_users()
            
            if not online_users:
                self.stdout.write(
                    self.style.WARNING('⚠️  当前没有在线用户')
                )
                return
            
            self.stdout.write(f"📱 当前在线用户数量: {len(online_users)}")
            self.stdout.write("-" * 50)
            
            for user_id in online_users:
                try:
                    user = User.objects.get(id=user_id)
                    session_id = proactive_engine.user_sessions.get(user_id, '未知')
                    self.stdout.write(
                        f"👤 {user.username} (ID: {user_id}, 会话: {session_id})"
                    )
                except User.DoesNotExist:
                    self.stdout.write(
                        f"❌ 用户ID {user_id} 不存在（已从在线列表移除）"
                    )
                    proactive_engine.remove_connected_user(user_id)
            
            # 发送测试消息
            test_message = options.get('send_test')
            if test_message:
                self.stdout.write(f"\n📤 向所有在线用户发送测试消息: {test_message}")
                sent_count = proactive_engine.send_proactive_message_to_all_online(
                    test_message, 'proactive'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ 成功发送给 {sent_count} 个用户')
                )
                
        except Exception as e:
            logger.error(f"查看在线用户失败: {e}")
            self.stdout.write(
                self.style.ERROR(f'❌ 操作失败: {e}')
            )
