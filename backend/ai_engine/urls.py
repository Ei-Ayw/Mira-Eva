"""
AI引擎URL配置
定义聊天相关的API端点
"""

from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    # 聊天相关API
    path('chat/', views.chat, name='chat'),
    path('conversations/', views.get_user_conversations, name='get_user_conversations'),
    path('conversations/create/', views.create_conversation, name='create_conversation'),
    path('conversations/<str:conversation_id>/', views.get_conversation_history, name='get_conversation_history'),
    path('conversations/<str:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
]
