from django.db import models
from django.contrib.auth.models import User


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

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.session_id}-{self.sender}-{self.content_type}"


