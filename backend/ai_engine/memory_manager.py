import logging
import json
from typing import Dict, List, Optional
from django.utils import timezone
from django.contrib.auth.models import User
from chat_system.models import UserMemory, ConversationHistory
from ai_engine.tencent_client import TencentDeepSeekClient

logger = logging.getLogger(__name__)

class MemoryManager:
    """记忆管理器 - 实现记忆的提取、存储和检索"""
    
    def __init__(self):
        self.memory_types = {
            'personal': '个人信息',
            'preference': '偏好',
            'relationship': '人际关系', 
            'event': '重要事件',
            'emotion': '情绪状态'
        }
    
    def extract_memories_from_conversation(self, user: User, conversation_text: str, session_id: str) -> List[Dict]:
        """从对话中提取记忆"""
        try:
            # 构建记忆提取提示词
            prompt = self._build_memory_extraction_prompt(conversation_text)
            
            # 调用AI提取记忆
            client = TencentDeepSeekClient()
            messages = [{"Role": "user", "Content": prompt}]
            result = client.chat(messages)
            response = result.get('text', '') if result.get('success') else ''
            
            # 解析AI响应
            extracted_memories = self._parse_memory_response(response)
            
            # 保存提取的记忆
            saved_memories = []
            for memory_data in extracted_memories:
                saved_memory = self._save_memory(user, memory_data, conversation_text)
                if saved_memory:
                    saved_memories.append(saved_memory)
            
            # 记录对话历史
            self._record_conversation_history(user, session_id, conversation_text, extracted_memories)
            
            logger.info(f"用户 {user.username} 提取到 {len(saved_memories)} 条记忆")
            return saved_memories
            
        except Exception as e:
            logger.error(f"记忆提取失败: {e}")
            return []
    
    def _build_memory_extraction_prompt(self, conversation_text: str) -> str:
        """构建记忆提取提示词"""
        return f"""你是Mira的记忆提取助手。请从以下对话中提取关于用户的重要信息，返回JSON格式。

对话内容："{conversation_text}"

请提取以下类型的信息：
1. 个人信息：姓名、年龄、职业、居住地等
2. 偏好：喜欢的食物、音乐、电影、活动等
3. 人际关系：家人、朋友、宠物等
4. 重要事件：生日、纪念日、计划等
5. 情绪状态：当前心情、压力源等

返回格式：
[
    {{
        "memory_type": "personal",
        "key": "pet_name", 
        "value": "小白",
        "context": "用户提到养了一只叫小白的狗",
        "importance_score": 0.8
    }}
]

注意：
- 只提取明确提到的信息
- importance_score: 0.1-1.0，越重要分数越高
- 如果对话中没有值得记忆的信息，返回空数组[]
- 确保JSON格式正确"""

    def _parse_memory_response(self, response: str) -> List[Dict]:
        """解析AI返回的记忆数据"""
        try:
            # 尝试直接解析JSON
            memories = json.loads(response)
            if isinstance(memories, list):
                return memories
            else:
                return []
        except json.JSONDecodeError:
            try:
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    memories = json.loads(json_match.group())
                    return memories if isinstance(memories, list) else []
            except:
                pass
        
        logger.warning(f"无法解析记忆响应: {response}")
        return []
    
    def _save_memory(self, user: User, memory_data: Dict, context: str) -> Optional[UserMemory]:
        """保存记忆到数据库"""
        try:
            memory_type = memory_data.get('memory_type', 'personal')
            key = memory_data.get('key', '')
            value = memory_data.get('value', '')
            importance_score = float(memory_data.get('importance_score', 0.5))
            
            if not key or not value:
                return None
            
            # 检查是否已存在相同记忆
            existing_memory, created = UserMemory.objects.get_or_create(
                user=user,
                key=key,
                defaults={
                    'memory_type': memory_type,
                    'value': value,
                    'context': context,
                    'importance_score': importance_score,
                    'is_active': True
                }
            )
            
            if not created:
                # 更新现有记忆
                existing_memory.value = value
                existing_memory.context = context
                existing_memory.importance_score = max(existing_memory.importance_score, importance_score)
                existing_memory.last_accessed = timezone.now()
                existing_memory.save()
            
            logger.info(f"记忆保存成功: {user.username}-{key}: {value}")
            return existing_memory
            
        except Exception as e:
            logger.error(f"保存记忆失败: {e}")
            return None
    
    def _record_conversation_history(self, user: User, session_id: str, content: str, extracted_memories: List[Dict]):
        """记录对话历史"""
        try:
            ConversationHistory.objects.create(
                user=user,
                session_id=session_id,
                message_content=content,
                sender='user',
                extracted_memories=extracted_memories
            )
        except Exception as e:
            logger.error(f"记录对话历史失败: {e}")
    
    def get_user_memories(self, user: User, memory_type: str = None, limit: int = 20) -> List[UserMemory]:
        """获取用户记忆"""
        try:
            queryset = UserMemory.objects.filter(user=user, is_active=True)
            
            if memory_type:
                queryset = queryset.filter(memory_type=memory_type)
            
            return list(queryset.order_by('-importance_score', '-last_accessed')[:limit])
            
        except Exception as e:
            logger.error(f"获取用户记忆失败: {e}")
            return []
    
    def build_memory_context(self, user: User, max_memories: int = 10) -> str:
        """构建记忆上下文，用于AI对话"""
        try:
            memories = self.get_user_memories(user, limit=max_memories)
            
            if not memories:
                return "用户信息：暂无记忆"
            
            context_parts = ["用户记忆信息："]
            
            # 按类型分组
            memory_groups = {}
            for memory in memories:
                memory_type = memory.memory_type
                if memory_type not in memory_groups:
                    memory_groups[memory_type] = []
                memory_groups[memory_type].append(memory)
            
            # 构建上下文
            for memory_type, memory_list in memory_groups.items():
                type_name = self.memory_types.get(memory_type, memory_type)
                context_parts.append(f"\n{type_name}：")
                
                for memory in memory_list:
                    context_parts.append(f"- {memory.key}: {memory.value}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"构建记忆上下文失败: {e}")
            return "用户信息：记忆加载失败"
    
    def update_memory_importance(self, user: User, key: str, importance_score: float):
        """更新记忆重要性"""
        try:
            memory = UserMemory.objects.get(user=user, key=key)
            memory.importance_score = max(memory.importance_score, importance_score)
            memory.last_accessed = timezone.now()
            memory.save()
            
            logger.info(f"记忆重要性更新: {user.username}-{key}: {importance_score}")
            
        except UserMemory.DoesNotExist:
            logger.warning(f"记忆不存在: {user.username}-{key}")
        except Exception as e:
            logger.error(f"更新记忆重要性失败: {e}")
    
    def delete_memory(self, user: User, key: str) -> bool:
        """删除记忆"""
        try:
            memory = UserMemory.objects.get(user=user, key=key)
            memory.is_active = False
            memory.save()
            
            logger.info(f"记忆已删除: {user.username}-{key}")
            return True
            
        except UserMemory.DoesNotExist:
            logger.warning(f"记忆不存在: {user.username}-{key}")
            return False
        except Exception as e:
            logger.error(f"删除记忆失败: {e}")
            return False
    
    def search_memories(self, user: User, query: str) -> List[UserMemory]:
        """搜索记忆"""
        try:
            memories = UserMemory.objects.filter(
                user=user,
                is_active=True
            ).filter(
                Q(key__icontains=query) | 
                Q(value__icontains=query) |
                Q(context__icontains=query)
            ).order_by('-importance_score', '-last_accessed')
            
            return list(memories)
            
        except Exception as e:
            logger.error(f"搜索记忆失败: {e}")
            return []
    
    def get_memory_statistics(self, user: User) -> Dict:
        """获取记忆统计信息"""
        try:
            total_memories = UserMemory.objects.filter(user=user, is_active=True).count()
            
            type_counts = {}
            for memory_type in self.memory_types.keys():
                count = UserMemory.objects.filter(
                    user=user, 
                    memory_type=memory_type, 
                    is_active=True
                ).count()
                type_counts[memory_type] = count
            
            recent_memories = UserMemory.objects.filter(
                user=user,
                is_active=True,
                last_accessed__gte=timezone.now() - timezone.timedelta(days=7)
            ).count()
            
            return {
                'total_memories': total_memories,
                'type_counts': type_counts,
                'recent_accessed': recent_memories,
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取记忆统计失败: {e}")
            return {
                'total_memories': 0,
                'type_counts': {},
                'recent_accessed': 0,
                'last_updated': timezone.now().isoformat()
            }

# 全局实例
memory_manager = MemoryManager()

if __name__ == "__main__":
    # 测试记忆管理器
    from django.contrib.auth.models import User
    
    manager = MemoryManager()
    
    # 测试记忆提取
    test_conversation = "我养了一只叫小白的狗，它很可爱。我喜欢吃火锅，特别是麻辣的。"
    
    try:
        user = User.objects.first()
        if user:
            memories = manager.extract_memories_from_conversation(user, test_conversation, "test_session")
            print(f"提取到 {len(memories)} 条记忆")
            
            # 测试记忆检索
            context = manager.build_memory_context(user)
            print(f"记忆上下文:\n{context}")
            
            # 测试统计
            stats = manager.get_memory_statistics(user)
            print(f"记忆统计: {stats}")
    except Exception as e:
        print(f"测试失败: {e}")
