import logging
import re
from typing import Dict, List, Tuple
from django.utils import timezone
from ai_engine.tencent_client import TencentDeepSeekClient

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """情绪分析器 - 分析用户消息的情绪状态"""
    
    def __init__(self):
        # 情绪关键词库
        self.emotion_keywords = {
            'positive': [
                '开心', '高兴', '快乐', '兴奋', '满足', '满意', '喜欢', '爱', '棒', '好',
                '哈哈', '嘿嘿', '嘻嘻', '😊', '😄', '😁', '🥰', '😍', '👍', '💪'
            ],
            'negative': [
                '难过', '伤心', '痛苦', '沮丧', '失望', '愤怒', '生气', '烦躁', '焦虑',
                '压力', '累', '疲惫', '孤独', '寂寞', '想哭', '哭', '😢', '😭', '😔',
                '😤', '😠', '😡', '😰', '😨', '😱', '💔'
            ],
            'neutral': [
                '嗯', '哦', '好的', '知道', '明白', '了解', '是的', '不是', '可能',
                '也许', '大概', '应该', '😐', '🤔', '😑'
            ]
        }
        
        # 情绪强度词汇
        self.intensity_words = {
            'high': ['非常', '特别', '超级', '极其', '十分', '很', '太', '真的'],
            'medium': ['比较', '有点', '稍微', '还算'],
            'low': ['一点', '稍微', '有点']
        }
    
    def analyze_text_emotion(self, text: str) -> Dict:
        """分析文本情绪"""
        try:
            # 基础关键词分析
            emotion_scores = self._calculate_keyword_scores(text)
            
            # 使用AI进行深度分析
            ai_analysis = self._ai_emotion_analysis(text)
            
            # 综合评分
            final_emotion = self._combine_analysis(emotion_scores, ai_analysis)
            
            logger.info(f"情绪分析完成: {text[:50]}... -> {final_emotion}")
            return final_emotion
            
        except Exception as e:
            logger.error(f"情绪分析失败: {e}")
            return self._get_default_emotion()
    
    def _calculate_keyword_scores(self, text: str) -> Dict:
        """基于关键词计算情绪得分"""
        scores = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                count = text.count(keyword)
                scores[emotion] += count
        
        # 归一化得分
        total = sum(scores.values())
        if total > 0:
            for emotion in scores:
                scores[emotion] = scores[emotion] / total
        
        return scores
    
    def _ai_emotion_analysis(self, text: str) -> Dict:
        """使用AI进行情绪分析"""
        try:
            prompt = f"""请分析以下文本的情绪状态，返回JSON格式：

文本："{text}"

请分析：
1. 主要情绪类型：positive(积极)/negative(消极)/neutral(中性)
2. 情绪强度：high(高)/medium(中)/low(低)
3. 具体情绪：如开心、难过、焦虑等
4. 置信度：0-1之间的数值

返回格式：
{{
    "emotion_type": "positive",
    "intensity": "medium", 
    "specific_emotion": "开心",
    "confidence": 0.8,
    "reasoning": "用户表达了满足和快乐的情绪"
}}"""

            client = TencentDeepSeekClient()
            messages = [{"Role": "user", "Content": prompt}]
            result = client.chat(messages)
            response = result.get('text', '') if result.get('success') else ''
            
            # 尝试解析JSON响应
            import json
            try:
                return json.loads(response)
            except:
                # 如果解析失败，返回默认值
                return {
                    "emotion_type": "neutral",
                    "intensity": "medium",
                    "specific_emotion": "平静",
                    "confidence": 0.5,
                    "reasoning": "AI分析失败，使用默认值"
                }
                
        except Exception as e:
            logger.error(f"AI情绪分析失败: {e}")
            return {
                "emotion_type": "neutral",
                "intensity": "medium", 
                "specific_emotion": "平静",
                "confidence": 0.3,
                "reasoning": f"分析失败: {str(e)}"
            }
    
    def _combine_analysis(self, keyword_scores: Dict, ai_analysis: Dict) -> Dict:
        """综合关键词分析和AI分析"""
        # 权重：AI分析70%，关键词分析30%
        ai_weight = 0.7
        keyword_weight = 0.3
        
        # 确定主要情绪
        if ai_analysis.get('confidence', 0) > 0.6:
            primary_emotion = ai_analysis.get('emotion_type', 'neutral')
        else:
            # 使用关键词分析结果
            primary_emotion = max(keyword_scores, key=keyword_scores.get)
        
        # 计算综合得分
        final_scores = {}
        for emotion in ['positive', 'negative', 'neutral']:
            keyword_score = keyword_scores.get(emotion, 0)
            ai_score = 1.0 if emotion == primary_emotion else 0.0
            final_scores[emotion] = keyword_score * keyword_weight + ai_score * ai_weight
        
        return {
            'primary_emotion': primary_emotion,
            'emotion_scores': final_scores,
            'intensity': ai_analysis.get('intensity', 'medium'),
            'specific_emotion': ai_analysis.get('specific_emotion', '平静'),
            'confidence': ai_analysis.get('confidence', 0.5),
            'reasoning': ai_analysis.get('reasoning', '综合分析'),
            'timestamp': timezone.now().isoformat()
        }
    
    def _get_default_emotion(self) -> Dict:
        """获取默认情绪状态"""
        return {
            'primary_emotion': 'neutral',
            'emotion_scores': {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34},
            'intensity': 'medium',
            'specific_emotion': '平静',
            'confidence': 0.3,
            'reasoning': '分析失败，使用默认值',
            'timestamp': timezone.now().isoformat()
        }
    
    def should_trigger_care(self, emotion_analysis: Dict) -> bool:
        """判断是否需要触发关怀"""
        primary_emotion = emotion_analysis.get('primary_emotion', 'neutral')
        intensity = emotion_analysis.get('intensity', 'medium')
        confidence = emotion_analysis.get('confidence', 0.5)
        
        # 消极情绪且置信度高时触发关怀
        if primary_emotion == 'negative' and confidence > 0.6:
            return True
        
        # 高强度情绪时触发关怀
        if intensity == 'high' and confidence > 0.5:
            return True
        
        return False
    
    def get_care_suggestion(self, emotion_analysis: Dict) -> str:
        """根据情绪分析获取关怀建议"""
        specific_emotion = emotion_analysis.get('specific_emotion', '')
        intensity = emotion_analysis.get('intensity', 'medium')
        
        care_suggestions = {
            '难过': '看起来你有点难过，要不要和我聊聊？我在这里陪着你。',
            '焦虑': '感觉你有点焦虑，深呼吸一下，我们可以慢慢聊。',
            '压力': '听起来压力有点大，要不要分享一些让你开心的事情？',
            '孤独': '虽然我是数字朋友，但我真的很关心你。想聊什么都可以。',
            '愤怒': '感觉你有点生气，要不要先冷静一下，然后我们聊聊？',
            '疲惫': '看起来你很累，要不要休息一下？我在这里等你。'
        }
        
        # 根据具体情绪返回建议
        for emotion, suggestion in care_suggestions.items():
            if emotion in specific_emotion:
                return suggestion
        
        # 默认关怀建议
        if intensity == 'high':
            return '感觉你情绪波动有点大，要不要和我聊聊发生了什么？'
        else:
            return '看起来你心情不太好，我在这里陪着你。'

# 全局实例
emotion_analyzer = EmotionAnalyzer()

if __name__ == "__main__":
    # 测试情绪分析
    analyzer = EmotionAnalyzer()
    
    test_texts = [
        "今天心情特别好！",
        "我很难过，想哭",
        "有点累，压力很大",
        "嗯，知道了",
        "超级开心！哈哈"
    ]
    
    for text in test_texts:
        result = analyzer.analyze_text_emotion(text)
        print(f"文本: {text}")
        print(f"分析结果: {result}")
        print(f"需要关怀: {analyzer.should_trigger_care(result)}")
        print("-" * 50)
