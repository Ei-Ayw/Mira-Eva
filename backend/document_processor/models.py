from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Document(models.Model):
    """上传的文档"""
    DOCUMENT_TYPES = [
        ('pdf', 'PDF'),
        ('docx', 'Word'),
        ('md', 'Markdown'),
        ('txt', 'Text'),
    ]
    
    STATUS_CHOICES = [
        ('uploading', '上传中'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255, verbose_name='文档标题')
    file = models.FileField(upload_to='documents/', verbose_name='文档文件')
    file_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES, verbose_name='文档类型')
    file_size = models.BigIntegerField(verbose_name='文件大小(字节)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading', verbose_name='处理状态')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    # 处理结果
    extracted_text = models.TextField(blank=True, verbose_name='提取的文本')
    summary = models.TextField(blank=True, verbose_name='文档摘要')
    keywords = models.JSONField(default=list, verbose_name='关键词')
    
    # 时间戳
    created_at = models.DateTimeField(default=timezone.now, verbose_name='上传时间')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='处理完成时间')
    
    class Meta:
        verbose_name = '文档'
        verbose_name_plural = '文档'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_file_type_display()})"


class DocumentChunk(models.Model):
    """文档分块，用于存储处理后的文本片段"""
    CHUNK_TYPES = [
        ('paragraph', '段落'),
        ('dialogue', '对话'),
        ('example', '示例'),
        ('instruction', '说明'),
        ('other', '其他'),
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_type = models.CharField(max_length=20, choices=CHUNK_TYPES, verbose_name='分块类型')
    content = models.TextField(verbose_name='内容')
    order = models.IntegerField(default=0, verbose_name='顺序')
    metadata = models.JSONField(default=dict, verbose_name='元数据')
    
    class Meta:
        verbose_name = '文档分块'
        verbose_name_plural = '文档分块'
        ordering = ['document', 'order']
    
    def __str__(self):
        return f"{self.document.title} - {self.get_chunk_type_display()} {self.order}"


class LearningPackage(models.Model):
    """学习包，将多个文档组合成学习材料"""
    PACKAGE_TYPES = [
        ('conversation', '对话示例'),
        ('knowledge', '知识库'),
        ('training', '训练材料'),
        ('reference', '参考资料'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_packages')
    name = models.CharField(max_length=255, verbose_name='包名称')
    description = models.TextField(blank=True, verbose_name='描述')
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPES, verbose_name='包类型')
    documents = models.ManyToManyField(Document, related_name='learning_packages', verbose_name='包含文档')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    # 统计信息
    total_chunks = models.IntegerField(default=0, verbose_name='总分块数')
    total_examples = models.IntegerField(default=0, verbose_name='总示例数')
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '学习包'
        verbose_name_plural = '学习包'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name
    
    def update_stats(self):
        """更新统计信息"""
        self.total_chunks = sum(doc.chunks.count() for doc in self.documents.all())
        self.total_examples = sum(doc.chunks.filter(chunk_type='example').count() for doc in self.documents.all())
        self.save()
