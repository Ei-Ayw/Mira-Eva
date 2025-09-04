from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from chat_system.proactive import proactive_engine
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '向指定用户发送主动消息'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'user_id',
            type=int,
            help='目标用户ID'
        )
        parser.add_argument(
            'message',
            type=str,
            help='要发送的消息内容'
        )
        parser.add_argument(
            '--type',
            type=str,
            default='proactive',
            choices=['proactive', 'greeting', 'care', 'share', 'reminder'],
            help='消息类型'
        )
        parser.add_argument(
            '--check-online',
            action='store_true',
            help='检查用户是否在线'
        )
    
    def handle(self, *args, **options):
        user_id = options['user_id']
        message = options['message']
        message_type = options['type']
        check_online = options['check_online']
        
        try:
            # 检查用户是否存在
            try:
                user = User.objects.get(id=user_id)
                self.stdout.write(f"目标用户: {user.username} (ID: {user.id})")
            except User.DoesNotExist:
                raise CommandError(f"用户ID {user_id} 不存在")
            
            # 检查用户是否在线
            if check_online:
                is_online = proactive_engine.is_user_online(user_id)
                self.stdout.write(f"用户在线状态: {'在线' if is_online else '离线'}")
                
                if not is_online:
                    self.stdout.write(
                        self.style.WARNING('⚠️  用户不在线，消息将不会发送')
                    )
                    return
            
            # 发送消息
            success = proactive_engine.send_message_to_user(
                user_id, message, message_type
            )
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ 消息发送成功: {message}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ 消息发送失败')
                )
                
        except Exception as e:
            logger.error(f"发送主动消息失败: {e}")
            raise CommandError(f'发送消息失败: {e}')
