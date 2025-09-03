import os
import logging
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import re

from .models import Document, DocumentChunk, LearningPackage
from .serializers import (
    DocumentSerializer, DocumentUploadSerializer,
    LearningPackageSerializer, LearningPackageCreateSerializer
)
from .processors import process_document

logger = logging.getLogger('document_processor')


class DocumentViewSet(viewsets.ModelViewSet):
    """文档管理视图集"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentUploadSerializer
        return DocumentSerializer
    
    def create(self, request, *args, **kwargs):
        """上传并处理文档"""
        try:
            # 获取上传的文件
            file_obj = request.FILES.get('file')
            title = request.data.get('title', file_obj.name if file_obj else '未命名文档')
            
            if not file_obj:
                return Response({'error': '请选择要上传的文件'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查文件类型
            file_ext = os.path.splitext(file_obj.name)[1].lower()
            supported_types = ['.pdf', '.docx', '.doc', '.md', '.markdown', '.txt']
            
            if file_ext not in supported_types:
                return Response({
                    'error': f'不支持的文件类型: {file_ext}。支持的类型: {", ".join(supported_types)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建文档记录
            document = Document.objects.create(
                user=request.user,
                title=title,
                file=file_obj,
                file_type=file_ext[1:],  # 去掉点号
                file_size=file_obj.size,
                status='uploading'
            )
            
            # 异步处理文档（这里简化为同步处理）
            try:
                self._process_document(document)
                document.status = 'completed'
                document.processed_at = timezone.now()
                document.save()
                
                logger.info(f"文档处理完成: {document.title}")
                
            except Exception as e:
                document.status = 'failed'
                document.error_message = str(e)
                document.save()
                
                logger.error(f"文档处理失败: {document.title}, 错误: {e}")
                return Response({
                    'error': f'文档处理失败: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 返回处理结果
            serializer = DocumentSerializer(document)
            return Response({
                'success': True,
                'message': '文档上传并处理成功',
                'document': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"文档上传失败: {e}")
            return Response({
                'error': f'文档上传失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _process_document(self, document: Document):
        """处理文档内容"""
        try:
            # 获取文件路径
            file_path = document.file.path
            
            # 处理文档
            extracted_text, chunks = process_document(file_path)
            
            # 保存提取的文本
            document.extracted_text = extracted_text
            
            # 生成摘要（简单的前100个字符）
            document.summary = extracted_text[:100] + "..." if len(extracted_text) > 100 else extracted_text
            
            # 提取关键词（简单的词频统计）
            words = re.findall(r'\w+', extracted_text.lower())
            word_freq = {}
            for word in words:
                if len(word) > 2:  # 过滤短词
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # 取前10个高频词作为关键词
            keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            document.keywords = [word for word, freq in keywords]
            
            document.save()
            
            # 创建文档分块
            for chunk_data in chunks:
                DocumentChunk.objects.create(
                    document=document,
                    chunk_type=chunk_data['chunk_type'],
                    content=chunk_data['content'],
                    order=chunk_data['order'],
                    metadata=chunk_data['metadata']
                )
            
            logger.info(f"文档 {document.title} 处理完成，创建了 {len(chunks)} 个分块")
            
        except Exception as e:
            logger.error(f"文档处理失败: {e}")
            raise
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """重新处理文档"""
        try:
            document = self.get_object()
            document.status = 'processing'
            document.error_message = ''
            document.save()
            
            # 删除旧的分块
            document.chunks.all().delete()
            
            # 重新处理
            self._process_document(document)
            
            document.status = 'completed'
            document.processed_at = timezone.now()
            document.save()
            
            serializer = DocumentSerializer(document)
            return Response({
                'success': True,
                'message': '文档重新处理成功',
                'document': serializer.data
            })
            
        except Exception as e:
            document.status = 'failed'
            document.error_message = str(e)
            document.save()
            
            return Response({
                'error': f'文档重新处理失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取文档统计信息"""
        user_docs = self.get_queryset()
        
        stats = {
            'total_documents': user_docs.count(),
            'by_status': {},
            'by_type': {},
            'total_size_mb': 0,
        }
        
        # 按状态统计
        for status_choice in Document.STATUS_CHOICES:
            count = user_docs.filter(status=status_choice[0]).count()
            stats['by_status'][status_choice[1]] = count
        
        # 按类型统计
        for type_choice in Document.DOCUMENT_TYPES:
            count = user_docs.filter(file_type=type_choice[0]).count()
            stats['by_type'][type_choice[1]] = count
        
        # 总文件大小
        total_size = sum(doc.file_size for doc in user_docs if doc.file_size)
        stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        
        return Response(stats)


class LearningPackageViewSet(viewsets.ModelViewSet):
    """学习包管理视图集"""
    queryset = LearningPackage.objects.all()
    serializer_class = LearningPackageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LearningPackage.objects.filter(user=self.request.user, is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LearningPackageCreateSerializer
        return LearningPackageSerializer
    
    def create(self, request, *args, **kwargs):
        """创建学习包"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 设置用户
        package = serializer.save(user=request.user)
        
        # 更新统计信息
        package.update_stats()
        
        result_serializer = LearningPackageSerializer(package)
        return Response({
            'success': True,
            'message': '学习包创建成功',
            'package': result_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def add_documents(self, request, pk=None):
        """向学习包添加文档"""
        package = self.get_object()
        document_ids = request.data.get('document_ids', [])
        
        if not document_ids:
            return Response({'error': '请选择要添加的文档'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取用户文档
        documents = Document.objects.filter(
            id__in=document_ids,
            user=request.user
        )
        
        # 添加到学习包
        package.documents.add(*documents)
        package.update_stats()
        
        serializer = LearningPackageSerializer(package)
        return Response({
            'success': True,
            'message': f'成功添加 {len(documents)} 个文档到学习包',
            'package': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def remove_documents(self, request, pk=None):
        """从学习包移除文档"""
        package = self.get_object()
        document_ids = request.data.get('document_ids', [])
        
        if not document_ids:
            return Response({'error': '请选择要移除的文档'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 从学习包移除
        package.documents.remove(*document_ids)
        package.update_stats()
        
        serializer = LearningPackageSerializer(package)
        return Response({
            'success': True,
            'message': f'成功从学习包移除 {len(document_ids)} 个文档',
            'package': serializer.data
        })
