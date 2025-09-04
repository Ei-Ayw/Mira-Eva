#!/usr/bin/env python
"""
Mira完整系统测试脚本
测试主动触发引擎、记忆系统、多模态交互等核心功能
"""

import os
import sys
import django
import asyncio
import json
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from chat_system.models import ChatSession, Message, UserMemory, UserActivity, ConversationHistory
from ai_engine.emotion_analyzer import emotion_analyzer
from ai_engine.memory_manager import memory_manager
from ai_engine.multimodal_handler import multimodal_handler
from chat_system.proactive import proactive_engine

def print_section(title):
    """打印测试章节标题"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def test_emotion_analyzer():
    """测试情绪分析器"""
    print_section("情绪分析器测试")
    
    test_texts = [
        "今天心情特别好！",
        "我很难过，想哭",
        "有点累，压力很大",
        "嗯，知道了",
        "超级开心！哈哈"
    ]
    
    for text in test_texts:
        result = emotion_analyzer.analyze_text_emotion(text)
        should_care = emotion_analyzer.should_trigger_care(result)
        care_suggestion = emotion_analyzer.get_care_suggestion(result)
        
        print(f"📝 文本: {text}")
        print(f"🎭 主要情绪: {result['primary_emotion']}")
        print(f"💪 强度: {result['intensity']}")
        print(f"🎯 具体情绪: {result['specific_emotion']}")
        print(f"📊 置信度: {result['confidence']:.2f}")
        print(f"💝 需要关怀: {should_care}")
        if should_care:
            print(f"💬 关怀建议: {care_suggestion}")
        print("-" * 40)

def test_memory_manager():
    """测试记忆管理器"""
    print_section("记忆管理器测试")
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    if created:
        print(f"✅ 创建测试用户: {user.username}")
    else:
        print(f"📋 使用现有用户: {user.username}")
    
    # 测试记忆提取
    test_conversation = "我养了一只叫小白的狗，它很可爱。我喜欢吃火锅，特别是麻辣的。"
    print(f"💬 测试对话: {test_conversation}")
    
    extracted_memories = memory_manager.extract_memories_from_conversation(
        user, test_conversation, "test_session"
    )
    
    print(f"🧠 提取到 {len(extracted_memories)} 条记忆:")
    for memory in extracted_memories:
        print(f"  - {memory.key}: {memory.value} (类型: {memory.memory_type}, 重要性: {memory.importance_score})")
    
    # 测试记忆检索
    context = memory_manager.build_memory_context(user)
    print(f"\n📚 记忆上下文:\n{context}")
    
    # 测试记忆统计
    stats = memory_manager.get_memory_statistics(user)
    print(f"\n📊 记忆统计: {stats}")

def test_multimodal_handler():
    """测试多模态处理器"""
    print_section("多模态处理器测试")
    
    # 测试图片生成
    print("🖼️ 测试图片生成...")
    image_result = multimodal_handler.generate_image("一只可爱的小猫")
    if image_result:
        print(f"✅ 图片生成成功: {image_result['image_url']}")
    else:
        print("❌ 图片生成失败")
    
    # 测试语音合成
    print("\n🎵 测试语音合成...")
    tts_result = multimodal_handler.text_to_speech("你好，我是Mira！")
    if tts_result:
        print(f"✅ 语音合成成功: {tts_result['audio_url']}")
    else:
        print("❌ 语音合成失败")
    
    # 测试图片分析
    print("\n🔍 测试图片分析...")
    analysis_result = multimodal_handler.analyze_image("https://example.com/image.jpg")
    if analysis_result:
        print(f"✅ 图片分析成功: {analysis_result['analysis']}")
    else:
        print("❌ 图片分析失败")

def test_proactive_engine():
    """测试主动触发引擎"""
    print_section("主动触发引擎测试")
    
    # 获取测试用户
    user = User.objects.filter(username='test_user').first()
    if not user:
        print("❌ 找不到测试用户")
        return
    
    # 测试触发条件判断
    print("🔍 测试触发条件判断...")
    
    # 测试问候触发
    should_greet = proactive_engine.should_trigger_greeting(user.id, None)
    print(f"👋 应该发送问候: {should_greet}")
    
    # 测试分享触发
    should_share = proactive_engine.should_trigger_share(user.id, None)
    print(f"💭 应该主动分享: {should_share}")
    
    # 测试消息生成
    print("\n💬 测试主动消息生成...")
    
    greeting_message = proactive_engine.generate_proactive_message('greeting', {
        'user_name': user.username,
        'time_of_day': '早上好'
    })
    print(f"👋 问候消息: {greeting_message}")
    
    care_message = proactive_engine.generate_proactive_message('care', {
        'user_name': user.username,
        'recent_emotion': '难过'
    })
    print(f"💝 关怀消息: {care_message}")
    
    share_message = proactive_engine.generate_proactive_message('share', {
        'user_name': user.username,
        'current_time': timezone.now()
    })
    print(f"💭 分享消息: {share_message}")

def test_database_models():
    """测试数据库模型"""
    print_section("数据库模型测试")
    
    # 获取测试用户
    user = User.objects.filter(username='test_user').first()
    if not user:
        print("❌ 找不到测试用户")
        return
    
    # 测试用户活动记录
    print("📝 测试用户活动记录...")
    activity = UserActivity.objects.create(
        user=user,
        activity_type='message',
        content='测试消息',
        metadata={'test': True}
    )
    print(f"✅ 创建活动记录: {activity}")
    
    # 测试对话历史
    print("\n💬 测试对话历史...")
    history = ConversationHistory.objects.create(
        user=user,
        session_id='test_session',
        message_content='这是一条测试消息',
        sender='user',
        emotion_analysis={'primary_emotion': 'neutral'},
        extracted_memories=[{'key': 'test', 'value': 'test_value'}]
    )
    print(f"✅ 创建对话历史: {history}")
    
    # 测试主动触发规则
    print("\n⚙️ 测试主动触发规则...")
    from chat_system.models import ProactiveTrigger
    trigger = ProactiveTrigger.objects.create(
        user=user,
        trigger_type='greeting',
        is_enabled=True,
        frequency_hours=6,
        conditions={'time_range': 'morning'}
    )
    print(f"✅ 创建触发规则: {trigger}")

def test_integration():
    """集成测试"""
    print_section("集成测试")
    
    # 获取测试用户
    user = User.objects.filter(username='test_user').first()
    if not user:
        print("❌ 找不到测试用户")
        return
    
    # 模拟完整的对话流程
    print("🔄 模拟完整对话流程...")
    
    # 1. 用户发送消息
    user_message = "我今天心情不太好，工作压力很大"
    print(f"👤 用户消息: {user_message}")
    
    # 2. 情绪分析
    emotion_result = emotion_analyzer.analyze_text_emotion(user_message)
    print(f"🎭 情绪分析: {emotion_result['primary_emotion']} ({emotion_result['intensity']})")
    
    # 3. 记忆提取
    memories = memory_manager.extract_memories_from_conversation(
        user, user_message, "integration_test"
    )
    print(f"🧠 提取记忆: {len(memories)} 条")
    
    # 4. 判断是否需要关怀
    should_care = emotion_analyzer.should_trigger_care(emotion_result)
    print(f"💝 需要关怀: {should_care}")
    
    if should_care:
        # 5. 生成关怀消息
        care_message = proactive_engine.generate_proactive_message('care', {
            'user_name': user.username,
            'emotion_analysis': emotion_result
        })
        print(f"🤖 Mira关怀: {care_message}")
    
    print("✅ 集成测试完成")

def cleanup_test_data():
    """清理测试数据"""
    print_section("清理测试数据")
    
    # 删除测试用户及其相关数据
    test_user = User.objects.filter(username='test_user').first()
    if test_user:
        # 删除相关数据
        UserMemory.objects.filter(user=test_user).delete()
        UserActivity.objects.filter(user=test_user).delete()
        ConversationHistory.objects.filter(user=test_user).delete()
        from chat_system.models import ProactiveTrigger
        ProactiveTrigger.objects.filter(user=test_user).delete()
        
        # 删除用户
        test_user.delete()
        print("✅ 测试数据清理完成")
    else:
        print("ℹ️ 没有找到测试数据")

def main():
    """主测试函数"""
    print("🚀 Mira完整系统测试开始")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 运行各项测试
        test_emotion_analyzer()
        test_memory_manager()
        test_multimodal_handler()
        test_proactive_engine()
        test_database_models()
        test_integration()
        
        print_section("测试总结")
        print("✅ 所有测试完成！")
        print("🎉 Mira系统核心功能运行正常")
        
        # 询问是否清理测试数据
        cleanup = input("\n🧹 是否清理测试数据？(y/N): ").lower().strip()
        if cleanup == 'y':
            cleanup_test_data()
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 测试结束")

if __name__ == "__main__":
    main()
