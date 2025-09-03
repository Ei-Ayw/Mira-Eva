"""
Mira-Eva 项目URL配置
数字孪生朋友AI系统的主要路由
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # 管理后台
    path('admin/', admin.site.urls),
    
    # JWT认证端点
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API路由
    path('api/chat/', include('chat_system.urls')),
    path('api/profile/', include('user_profile.urls')),
    path('api/settings/', include('user_settings.urls')),
    path('api/ai/', include('ai_engine.urls')),
    
    # 根端点
    path('', lambda request: {
        'message': '欢迎使用 Mira-Eva AI聊天系统！',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': {
            'chat': '/api/chat/',
            'profile': '/api/profile/',
            'settings': '/api/settings/',
            'ai': '/api/ai/',
            'websocket': '/ws/chat/{session_id}/',
            'auth': '/api/token/',
        }
    }),
]

# 开发环境下的媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
