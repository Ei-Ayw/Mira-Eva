from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username}-{self.session_id}"


class Message(models.Model):
    CONTENT_TYPES = [
        ('text', '文字'),
        ('image', '图片'),
        ('audio', '语音'),
    ]
    SENDER_TYPES = [
        ('user', '用户'),
        ('ai', 'AI'),
    ]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='text')
    sender = models.CharField(max_length=20, choices=SENDER_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_proactive = models.BooleanField(default=False)  # 是否为主动触发消息
    emotion_score = models.FloatField(null=True, blank=True)  # 情绪分析得分
    metadata = models.JSONField(default=dict, blank=True)  # 额外元数据

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        try:
            sid = getattr(self.session, 'id', 'unknown')
        except Exception:
            sid = 'unknown'
        return f"{sid}-{self.sender}-{self.content_type}"


class UserActivity(models.Model):
    """用户活动记录 - 用于主动触发分析"""
    ACTIVITY_TYPES = [
        ('login', '登录'),
        ('message', '发送消息'),
        ('upload', '上传文件'),
        ('view_profile', '查看资料'),
        ('settings_change', '修改设置'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    content = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username}-{self.activity_type}"


class UserMemory(models.Model):
    """用户记忆库 - 存储AI对用户的了解"""
    MEMORY_TYPES = [
        ('personal', '个人信息'),
        ('preference', '偏好'),
        ('relationship', '人际关系'),
        ('event', '重要事件'),
        ('emotion', '情绪状态'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memories')
    memory_type = models.CharField(max_length=20, choices=MEMORY_TYPES)
    key = models.CharField(max_length=100)  # 记忆键，如 "pet_name"
    value = models.TextField()  # 记忆值，如 "小白"
    context = models.TextField(blank=True)  # 上下文信息
    importance_score = models.FloatField(default=1.0)  # 重要性评分
    last_accessed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'key']
        ordering = ['-importance_score', '-last_accessed']

    def __str__(self):
        return f"{self.user.username}-{self.key}: {self.value}"


class ProactiveTrigger(models.Model):
    """主动触发规则配置"""
    TRIGGER_TYPES = [
        ('greeting', '问候'),
        ('care', '关怀'),
        ('share', '分享'),
        ('reminder', '提醒'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proactive_triggers')
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES)
    is_enabled = models.BooleanField(default=True)
    frequency_hours = models.IntegerField(default=6)  # 触发频率（小时）
    last_triggered = models.DateTimeField(null=True, blank=True)
    conditions = models.JSONField(default=dict, blank=True)  # 触发条件
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'trigger_type']

    def __str__(self):
        return f"{self.user.username}-{self.trigger_type}"


class ConversationHistory(models.Model):
    """对话历史 - 用于上下文理解"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_history')
    session_id = models.CharField(max_length=100)
    message_content = models.TextField()
    sender = models.CharField(max_length=20)  # 'user' or 'ai'
    timestamp = models.DateTimeField(auto_now_add=True)
    emotion_analysis = models.JSONField(default=dict, blank=True)  # 情绪分析结果
    extracted_memories = models.JSONField(default=list, blank=True)  # 提取的记忆

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username}-{self.sender}-{self.timestamp}"


