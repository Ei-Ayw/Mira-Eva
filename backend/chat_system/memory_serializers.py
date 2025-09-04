from rest_framework import serializers
from .models import UserMemory

class UserMemorySerializer(serializers.ModelSerializer):
    """用户记忆序列化器"""
    
    memory_type_display = serializers.CharField(source='get_memory_type_display', read_only=True)
    importance_percentage = serializers.SerializerMethodField()
    days_since_created = serializers.SerializerMethodField()
    days_since_accessed = serializers.SerializerMethodField()
    
    class Meta:
        model = UserMemory
        fields = [
            'id', 'memory_type', 'memory_type_display', 'key', 'value', 
            'context', 'importance_score', 'importance_percentage',
            'last_accessed', 'created_at', 'is_active',
            'days_since_created', 'days_since_accessed'
        ]
        read_only_fields = ['id', 'created_at', 'last_accessed']
    
    def get_importance_percentage(self, obj):
        """获取重要性百分比"""
        return round(obj.importance_score * 100, 1)
    
    def get_days_since_created(self, obj):
        """获取创建天数"""
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        return delta.days
    
    def get_days_since_accessed(self, obj):
        """获取最后访问天数"""
        from django.utils import timezone
        delta = timezone.now() - obj.last_accessed
        return delta.days
    
    def validate_importance_score(self, value):
        """验证重要性评分"""
        if not isinstance(value, (int, float)):
            raise serializers.ValidationError("重要性评分必须是数字")
        
        if not (0 <= value <= 1):
            raise serializers.ValidationError("重要性评分必须在0-1之间")
        
        return value
    
    def validate_key(self, value):
        """验证记忆键"""
        if not value or not value.strip():
            raise serializers.ValidationError("记忆键不能为空")
        
        # 检查键名格式
        if len(value) > 100:
            raise serializers.ValidationError("记忆键长度不能超过100个字符")
        
        return value.strip()
    
    def validate_value(self, value):
        """验证记忆值"""
        if not value or not value.strip():
            raise serializers.ValidationError("记忆值不能为空")
        
        return value.strip()
    
    def validate(self, attrs):
        """整体验证"""
        # 检查同一用户下是否已存在相同的键
        user = self.context['request'].user
        key = attrs.get('key')
        
        if key:
            existing_memory = UserMemory.objects.filter(
                user=user,
                key=key,
                is_active=True
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_memory.exists():
                raise serializers.ValidationError({
                    'key': f'记忆键 "{key}" 已存在'
                })
        
        return attrs

class MemoryStatsSerializer(serializers.Serializer):
    """记忆统计序列化器"""
    
    total_memories = serializers.IntegerField()
    type_counts = serializers.DictField()
    recent_accessed = serializers.IntegerField()
    last_updated = serializers.DateTimeField()

class MemorySearchSerializer(serializers.Serializer):
    """记忆搜索序列化器"""
    
    query = serializers.CharField(max_length=200, help_text="搜索关键词")
    memory_type = serializers.ChoiceField(
        choices=UserMemory.MEMORY_TYPES,
        required=False,
        help_text="记忆类型筛选"
    )
    limit = serializers.IntegerField(
        default=20,
        min_value=1,
        max_value=100,
        help_text="返回结果数量限制"
    )

class MemoryExtractionSerializer(serializers.Serializer):
    """记忆提取序列化器"""
    
    text = serializers.CharField(help_text="要分析的对话文本")
    session_id = serializers.CharField(
        max_length=100,
        required=False,
        help_text="会话ID"
    )
