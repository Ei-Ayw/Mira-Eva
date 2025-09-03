"""
AI引擎数据模型
定义AI对话、用户会话等核心数据结构
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class AIConversation(models.Model):
    """AI对话会话模型"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    session_id = models.CharField(max_length=100, unique=True, verbose_name='会话ID')
    ai_name = models.CharField(max_length=50, default='Mira', verbose_name='AI名称')
    ai_avatar = models.URLField(default='/images/ai-avatar.png', verbose_name='AI头像')
    
    # 会话状态
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    last_interaction = models.DateTimeField(auto_now=True, verbose_name='最后交互时间')
    
    # 会话设置
    ai_personality = models.JSONField(default=dict, verbose_name='AI个性设置')
    conversation_style = models.CharField(
        max_length=20, 
        choices=[
            ('friendly', '友好'),
            ('professional', '专业'),
            ('casual', '随意'),
            ('romantic', '浪漫'),
        ],
        default='friendly',
        verbose_name='对话风格'
    )
    
    class Meta:
        verbose_name = 'AI对话会话'
        verbose_name_plural = 'AI对话会话'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.ai_name} ({self.session_id})"
    
    def get_ai_personality(self):
        """获取AI个性设置"""
        return self.ai_personality or {
            'name': self.ai_name,
            'personality': 'friendly',
            'interests': ['聊天', '音乐', '电影'],
            'speaking_style': 'casual'
        }

class AIMessage(models.Model):
    """AI对话消息模型"""
    
    MESSAGE_TYPES = [
        ('text', '文字'),
        ('audio', '语音'),
        ('image', '图片'),
        ('video', '视频'),
        ('system', '系统消息'),
    ]
    
    SENDER_TYPES = [
        ('user', '用户'),
        ('ai', 'AI'),
        ('system', '系统'),
    ]
    
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, verbose_name='对话会话')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, verbose_name='消息类型')
    sender = models.CharField(max_length=20, choices=SENDER_TYPES, verbose_name='发送者')
    
    # 消息内容
    content = models.TextField(verbose_name='消息内容')
    content_url = models.URLField(blank=True, null=True, verbose_name='媒体内容URL')
    
    # 消息元数据
    metadata = models.JSONField(default=dict, verbose_name='消息元数据')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    
    # 消息状态
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    is_processed = models.BooleanField(default=False, verbose_name='是否已处理')
    
    class Meta:
        verbose_name = 'AI对话消息'
        verbose_name_plural = 'AI对话消息'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender} - {self.message_type} - {self.timestamp}"
    
    def get_content_preview(self):
        """获取消息内容预览"""
        if self.message_type == 'text':
            return self.content[:50] + '...' if len(self.content) > 50 else self.content
        elif self.message_type == 'audio':
            duration = self.metadata.get('duration', 0)
            return f"语音消息 ({duration}秒)"
        elif self.message_type == 'image':
            return "图片消息"
        elif self.message_type == 'video':
            return "视频消息"
        else:
            return "系统消息"
    
    def get_metadata(self):
        """获取消息元数据"""
        return self.metadata or {}

class AIResponse(models.Model):
    """AI回复模型"""
    
    message = models.OneToOneField(AIMessage, on_delete=models.CASCADE, verbose_name='原始消息')
    
    # 回复内容
    response_content = models.TextField(verbose_name='回复内容')
    response_type = models.CharField(max_length=20, choices=AIMessage.MESSAGE_TYPES, verbose_name='回复类型')
    response_url = models.URLField(blank=True, null=True, verbose_name='回复媒体URL')
    
    # 回复质量
    confidence_score = models.FloatField(default=0.8, verbose_name='置信度')
    response_time = models.FloatField(default=0.0, verbose_name='响应时间(秒)')
    
    # 生成信息
    model_used = models.CharField(max_length=100, default='virtual', verbose_name='使用的模型')
    generation_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0.0, verbose_name='生成成本')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='生成时间')
    
    class Meta:
        verbose_name = 'AI回复'
        verbose_name_plural = 'AI回复'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"AI回复 - {self.message.id} - {self.response_type}"

class AIPersonality(models.Model):
    """AI个性配置模型"""
    
    name = models.CharField(max_length=50, unique=True, verbose_name='个性名称')
    description = models.TextField(verbose_name='个性描述')
    
    # 个性特征
    personality_traits = models.JSONField(default=dict, verbose_name='个性特征')
    speaking_style = models.JSONField(default=dict, verbose_name='说话风格')
    interests = models.JSONField(default=list, verbose_name='兴趣爱好')
    
    # 系统提示词
    system_prompt = models.TextField(verbose_name='系统提示词')
    
    # 配置状态
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'AI个性配置'
        verbose_name_plural = 'AI个性配置'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_personality_config(self):
        """获取个性配置"""
        return {
            'name': self.name,
            'description': self.description,
            'traits': self.personality_traits,
            'speaking_style': self.speaking_style,
            'interests': self.interests,
            'system_prompt': self.system_prompt
        }
