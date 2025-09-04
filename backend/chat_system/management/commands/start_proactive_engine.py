from django.core.management.base import BaseCommand
from chat_system.proactive import start_proactive_engine
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '启动Mira主动触发引擎'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='以守护进程模式运行',
        )
    
    def handle(self, *args, **options):
        try:
            self.stdout.write(
                self.style.SUCCESS('🚀 启动Mira主动触发引擎...')
            )
            
            if options['daemon']:
                self.stdout.write('以守护进程模式运行...')
                # 这里可以集成更复杂的进程管理
                start_proactive_engine()
            else:
                self.stdout.write('以交互模式运行...')
                # 运行一次主动任务
                from chat_system.proactive import proactive_engine
                proactive_engine.run_daily_tasks()
                self.stdout.write(
                    self.style.SUCCESS('✅ 主动触发引擎任务执行完成')
                )
                
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n⚠️  主动触发引擎已停止')
            )
        except Exception as e:
            logger.error(f"启动主动触发引擎失败: {e}")
            self.stdout.write(
                self.style.ERROR(f'❌ 启动失败: {e}')
            )
