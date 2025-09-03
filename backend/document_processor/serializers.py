from rest_framework import serializers
from .models import Document, DocumentChunk, LearningPackage


class DocumentChunkSerializer(serializers.ModelSerializer):
    """文档分块序列化器"""
    chunk_type_display = serializers.CharField(source='get_chunk_type_display', read_only=True)
    
    class Meta:
        model = DocumentChunk
        fields = ['id', 'chunk_type', 'chunk_type_display', 'content', 'order', 'metadata']


class DocumentSerializer(serializers.ModelSerializer):
    """文档序列化器"""
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    chunks = DocumentChunkSerializer(many=True, read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file', 'file_type', 'file_type_display', 'file_size', 'file_size_mb',
            'status', 'status_display', 'error_message', 'extracted_text', 'summary', 'keywords',
            'created_at', 'processed_at', 'chunks'
        ]
        read_only_fields = ['file_size', 'status', 'error_message', 'extracted_text', 'summary', 'keywords', 'processed_at', 'chunks']
    
    def get_file_size_mb(self, obj):
        """计算文件大小（MB）"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return 0


class DocumentUploadSerializer(serializers.ModelSerializer):
    """文档上传序列化器"""
    class Meta:
        model = Document
        fields = ['title', 'file']


class LearningPackageSerializer(serializers.ModelSerializer):
    """学习包序列化器"""
    package_type_display = serializers.CharField(source='get_package_type_display', read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPackage
        fields = [
            'id', 'name', 'description', 'package_type', 'package_type_display',
            'is_active', 'total_chunks', 'total_examples', 'documents', 'document_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total_chunks', 'total_examples', 'created_at', 'updated_at']
    
    def get_document_count(self, obj):
        """获取文档数量"""
        return obj.documents.count()


class LearningPackageCreateSerializer(serializers.ModelSerializer):
    """学习包创建序列化器"""
    document_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = LearningPackage
        fields = ['name', 'description', 'package_type', 'document_ids']
    
    def create(self, validated_data):
        document_ids = validated_data.pop('document_ids', [])
        package = LearningPackage.objects.create(**validated_data)
        
        if document_ids:
            documents = Document.objects.filter(id__in=document_ids, user=self.context['request'].user)
            package.documents.set(documents)
            package.update_stats()
        
        return package
