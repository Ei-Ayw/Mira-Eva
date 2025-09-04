from django.apps import AppConfig
import threading
import logging

logger = logging.getLogger(__name__)

class ChatSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat_system'
    
    def ready(self):
        """Django应用启动时自动运行"""
        # 避免在迁移时运行
        import sys
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
            
        # 启动主动触发引擎后台线程
        self.start_proactive_engine()
    
    def start_proactive_engine(self):
        """启动主动触发引擎后台线程"""
        try:
            from .proactive import proactive_engine
            
            def run_engine():
                """在后台线程中运行主动触发引擎"""
                try:
                    logger.info("🚀 启动Mira主动触发引擎后台服务...")
                    proactive_engine.start_background_tasks()
                except Exception as e:
                    logger.error(f"主动触发引擎运行失败: {e}")
            
            # 创建并启动后台线程
            engine_thread = threading.Thread(target=run_engine, daemon=True)
            engine_thread.start()
            
            logger.info("✅ Mira主动触发引擎已启动")
            
        except Exception as e:
            logger.error(f"启动主动触发引擎失败: {e}")
    verbose_name = '聊天系统'


