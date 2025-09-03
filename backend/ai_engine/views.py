"""
AI引擎API视图
处理聊天请求，返回AI回复
"""

import json
import logging
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .core import AIEngine
from .models import AIConversation, AIMessage, AIResponse

logger = logging.getLogger(__name__)

# 初始化AI引擎
ai_engine = AIEngine()

@api_view(['POST'])
@permission_classes([])  # 暂时移除认证要求，用于开发测试
def chat(request):
    """
    聊天API端点
    
    接收用户消息，返回AI回复
    """
    try:
        # 获取请求数据
        data = request.data
        # 暂时使用虚拟用户，用于开发测试
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@example.com'}
        )
        
        # 验证必要字段
        if 'content' not in data or 'message_type' not in data:
            return Response({
                'success': False,
                'error': '缺少必要字段：content 或 message_type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取或创建对话会话
        conversation, created = AIConversation.objects.get_or_create(
            user=user,
            defaults={
                'session_id': f"session_{user.id}_{int(time.time())}",
                'ai_name': 'Mira',
                'ai_avatar': '/images/ai-avatar.png'
            }
        )
        
        # 创建用户消息记录
        user_message = AIMessage.objects.create(
            conversation=conversation,
            message_type=data.get('message_type', 'text'),
            sender='user',
            content=data['content'],
            content_url=data.get('content_url', ''),
            metadata=data.get('metadata', {})
        )
        
        # 调用AI引擎处理
        ai_response_data = ai_engine.process_user_input(
            user_id=user.id,
            input_data={
                'content': data['content'],
                'message_type': data.get('message_type', 'text'),
                'metadata': data.get('metadata', {})
            }
        )
        
        if ai_response_data.get('success', False):
            # 创建AI回复记录
            ai_message = AIMessage.objects.create(
                conversation=conversation,
                message_type=ai_response_data.get('type', 'text'),
                sender='ai',
                content=ai_response_data.get('content', ''),
                content_url=ai_response_data.get('content_url', ''),
                metadata={
                    'intent': ai_response_data.get('intent', ''),
                    'emotion': ai_response_data.get('emotion', ''),
                    'confidence': ai_response_data.get('confidence', 0.8),
                    'response_time': ai_response_data.get('response_time', 0)
                }
            )
            
            # 创建AI回复记录
            AIResponse.objects.create(
                message=ai_message,
                response_content=ai_response_data.get('content', ''),
                response_type=ai_response_data.get('type', 'text'),
                response_url=ai_response_data.get('content_url', ''),
                confidence_score=ai_response_data.get('confidence', 0.8),
                response_time=ai_response_data.get('response_time', 0),
                model_used='virtual'  # 当前使用虚拟实现
            )
            
            # 更新会话最后交互时间
            conversation.save()
            
            # 返回AI回复
            return Response({
                'success': True,
                'message_id': ai_message.id,
                'response': {
                    'type': ai_response_data.get('type', 'text'),
                    'content': ai_response_data.get('content', ''),
                    'content_url': ai_response_data.get('content_url', ''),
                    'metadata': ai_response_data.get('metadata', {})
                },
                'conversation_id': conversation.session_id
            })
        else:
            return Response({
                'success': False,
                'error': ai_response_data.get('error', 'AI处理失败')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"聊天API错误: {str(e)}")
        return Response({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([])  # 暂时移除认证要求，用于开发测试
def get_conversation_history(request):
    """
    获取对话历史
    
    返回用户与AI的聊天记录
    """
    try:
        # 暂时使用虚拟用户，用于开发测试
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@example.com'}
        )
        conversation_id = request.GET.get('conversation_id')
        
        if conversation_id:
            # 获取指定会话的历史记录
            try:
                conversation = AIConversation.objects.get(
                    user=user,
                    session_id=conversation_id
                )
            except AIConversation.DoesNotExist:
                return Response({
                    'success': False,
                    'error': '会话不存在'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # 获取最新的活跃会话
            conversation = AIConversation.objects.filter(
                user=user,
                is_active=True
            ).order_by('-updated_at').first()
            
            if not conversation:
                return Response({
                    'success': False,
                    'error': '没有找到活跃的对话会话'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # 获取消息历史
        messages = AIMessage.objects.filter(
            conversation=conversation
        ).order_by('timestamp')
        
        # 格式化消息数据
        message_list = []
        for msg in messages:
            message_data = {
                'id': msg.id,
                'type': msg.message_type,
                'sender': msg.sender,
                'content': msg.content,
                'content_url': msg.content_url,
                'timestamp': msg.timestamp.isoformat(),
                'metadata': msg.get_metadata()
            }
            message_list.append(message_data)
        
        return Response({
            'success': True,
            'conversation': {
                'id': conversation.session_id,
                'ai_name': conversation.ai_name,
                'ai_avatar': conversation.ai_avatar,
                'created_at': conversation.created_at.isoformat(),
                'last_interaction': conversation.last_interaction.isoformat()
            },
            'messages': message_list
        })
        
    except Exception as e:
        logger.error(f"获取对话历史错误: {str(e)}")
        return Response({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([])  # 暂时移除认证要求，用于开发测试
def create_conversation(request):
    """
    创建新的对话会话
    """
    try:
        # 暂时使用虚拟用户，用于开发测试
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@example.com'}
        )
        data = request.data
        
        # 生成会话ID
        import time
        session_id = f"session_{user.id}_{int(time.time())}"
        
        # 创建新会话
        conversation = AIConversation.objects.create(
            user=user,
            session_id=session_id,
            ai_name=data.get('ai_name', 'Mira'),
            ai_avatar=data.get('ai_avatar', '/images/ai-avatar.png'),
            conversation_style=data.get('conversation_style', 'friendly'),
            ai_personality=data.get('ai_personality', {})
        )
        
        return Response({
            'success': True,
            'conversation': {
                'id': conversation.session_id,
                'ai_name': conversation.ai_name,
                'ai_avatar': conversation.ai_avatar,
                'created_at': conversation.created_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"创建对话会话错误: {str(e)}")
        return Response({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([])  # 暂时移除认证要求，用于开发测试
def get_user_conversations(request):
    """
    获取用户的所有对话会话
    """
    try:
        # 暂时使用虚拟用户，用于开发测试
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@example.com'}
        )
        
        conversations = AIConversation.objects.filter(
            user=user
        ).order_by('-updated_at')
        
        conversation_list = []
        for conv in conversations:
            # 获取每个会话的最新消息
            latest_message = AIMessage.objects.filter(
                conversation=conv
            ).order_by('-timestamp').first()
            
            conversation_data = {
                'id': conv.session_id,
                'ai_name': conv.ai_name,
                'ai_avatar': conv.ai_avatar,
                'conversation_style': conv.conversation_style,
                'is_active': conv.is_active,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'last_interaction': conv.last_interaction.isoformat(),
                'latest_message': latest_message.get_content_preview() if latest_message else ''
            }
            conversation_list.append(conversation_data)
        
        return Response({
            'success': True,
            'conversations': conversation_list
        })
        
    except Exception as e:
        logger.error(f"获取用户对话会话错误: {str(e)}")
        return Response({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([])  # 暂时移除认证要求，用于开发测试
def delete_conversation(request, conversation_id):
    """
    删除对话会话
    """
    try:
        # 暂时使用虚拟用户，用于开发测试
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@example.com'}
        )
        
        try:
            conversation = AIConversation.objects.get(
                user=user,
                session_id=conversation_id
            )
        except AIConversation.DoesNotExist:
            return Response({
                'success': False,
                'error': '会话不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 删除会话（级联删除相关消息）
        conversation.delete()
        
        return Response({
            'success': True,
            'message': '会话删除成功'
        })
        
    except Exception as e:
        logger.error(f"删除对话会话错误: {str(e)}")
        return Response({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
