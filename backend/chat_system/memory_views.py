from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Q
from .models import UserMemory
from .memory_serializers import UserMemorySerializer
from ai_engine.memory_manager import memory_manager
import logging

logger = logging.getLogger(__name__)

class UserMemoryViewSet(viewsets.ModelViewSet):
    """用户记忆管理API"""
    serializer_class = UserMemorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的记忆"""
        return UserMemory.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-importance_score', '-last_accessed')
    
    def perform_create(self, serializer):
        """创建记忆时设置用户"""
        serializer.save(user=self.request.user)
        logger.info(f"用户 {self.request.user.username} 创建记忆: {serializer.validated_data.get('key')}")
    
    def perform_update(self, serializer):
        """更新记忆时记录日志"""
        logger.info(f"用户 {self.request.user.username} 更新记忆: {serializer.instance.key}")
        serializer.save()
    
    def perform_destroy(self, instance):
        """软删除记忆"""
        instance.is_active = False
        instance.save()
        logger.info(f"用户 {self.request.user.username} 删除记忆: {instance.key}")
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取记忆统计信息"""
        try:
            stats = memory_manager.get_memory_statistics(request.user)
            return Response(stats)
        except Exception as e:
            logger.error(f"获取记忆统计失败: {e}")
            return Response(
                {'error': '获取统计信息失败'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """搜索记忆"""
        try:
            query = request.data.get('query', '')
            if not query:
                return Response({'error': '搜索词不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
            memories = memory_manager.search_memories(request.user, query)
            serializer = self.get_serializer(memories, many=True)
            
            return Response({
                'results': serializer.data,
                'total': len(memories),
                'query': query
            })
        except Exception as e:
            logger.error(f"搜索记忆失败: {e}")
            return Response(
                {'error': '搜索失败'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def extract_from_conversation(self, request):
        """从对话中提取记忆"""
        try:
            conversation_text = request.data.get('text', '')
            session_id = request.data.get('session_id', '')
            
            if not conversation_text:
                return Response(
                    {'error': '对话文本不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 提取记忆
            extracted_memories = memory_manager.extract_memories_from_conversation(
                request.user, conversation_text, session_id
            )
            
            serializer = self.get_serializer(extracted_memories, many=True)
            
            return Response({
                'success': True,
                'extracted_memories': serializer.data,
                'count': len(extracted_memories)
            })
            
        except Exception as e:
            logger.error(f"提取记忆失败: {e}")
            return Response(
                {'error': '提取记忆失败'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def update_importance(self, request, pk=None):
        """更新记忆重要性"""
        try:
            memory = self.get_object()
            importance_score = request.data.get('importance_score', 0.5)
            
            if not isinstance(importance_score, (int, float)) or not (0 <= importance_score <= 1):
                return Response(
                    {'error': '重要性评分必须在0-1之间'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            memory_manager.update_memory_importance(
                request.user, memory.key, importance_score
            )
            
            return Response({'success': True})
            
        except Exception as e:
            logger.error(f"更新记忆重要性失败: {e}")
            return Response(
                {'error': '更新失败'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def context(self, request):
        """获取记忆上下文"""
        try:
            max_memories = int(request.query_params.get('max_memories', 10))
            context = memory_manager.build_memory_context(request.user, max_memories)
            
            return Response({
                'context': context,
                'max_memories': max_memories
            })
            
        except Exception as e:
            logger.error(f"获取记忆上下文失败: {e}")
            return Response(
                {'error': '获取上下文失败'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """按类型获取记忆"""
        try:
            memory_type = request.query_params.get('type', '')
            limit = int(request.query_params.get('limit', 20))
            
            memories = memory_manager.get_user_memories(
                request.user, memory_type, limit
            )
            
            serializer = self.get_serializer(memories, many=True)
            
            return Response({
                'results': serializer.data,
                'type': memory_type,
                'count': len(memories)
            })
            
        except Exception as e:
            logger.error(f"按类型获取记忆失败: {e}")
            return Response(
                {'error': '获取记忆失败'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
