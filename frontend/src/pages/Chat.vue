<template>
  <div class="chat-page">
    <!-- 顶部状态栏 -->
    <div class="status-bar">
      <span class="time">9:41</span>
      <div class="status-icons">
        <span class="status-icon">⋮</span>
      </div>
    </div>

    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="header-content">
        <div class="ai-profile">
          <div class="avatar">
            <RobotOutlined class="avatar-icon" />
          </div>
          <div class="ai-info">
            <h3 class="ai-name">Mira</h3>
            <p class="ai-status">Online • Always here for you</p>
          </div>
        </div>
        <div class="header-actions">
          <button @click="goToProfile" class="action-btn">
            <UserOutlined class="action-icon" />
          </button>
          <button @click="goToSettings" class="action-btn">
            <SettingOutlined class="action-icon" />
          </button>
        </div>
      </div>
    </div>

    <!-- 聊天消息区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="isAiTyping" class="typing-indicator">
        <span class="dot"></span><span class="dot"></span><span class="dot"></span>
      </div>
      <div 
        v-for="message in messages" 
        :key="message.id"
        :class="['message-wrapper', message.sender]"
      >
        <!-- AI消息 -->
        <div v-if="message.sender === 'ai'" class="message ai-message">
          <div class="message-avatar">
            <img :src="aiAvatar" @error="onAiAvatarError" class="avatar-img" alt="Mira" />
          </div>
          <div class="message-content">
            <!-- 文字消息 -->
            <div v-if="message.contentType === 'text'" class="text-message">
              {{ message.content }}
            </div>
            
            <!-- 语音消息 -->
            <div v-else-if="message.contentType === 'audio'" class="audio-message">
              <div class="audio-player">
                <SoundOutlined class="audio-icon" />
                <div class="audio-wave">
                  <span v-for="i in 5" :key="i" class="wave-bar"></span>
                </div>
                <span class="duration">{{ formatDuration(message.duration) }}</span>
              </div>
            </div>
            
            <!-- 图片消息 -->
            <div v-else-if="message.contentType === 'image'" class="image-message">
              <div class="image-content">
                <p v-if="shouldShowImageText(message.text)" class="image-text">{{ imageTextForDisplay(message.text) }}</p>
                <img 
                  :src="message.content" 
                  :alt="message.alt || imageTextForDisplay(message.text)" 
                  @click="previewImage(message.content)"
                  @error="handleImageError"
                  class="message-image"
                />
              </div>
            </div>
            
            <!-- 时间戳（AI） -->
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>

        <!-- 用户消息 -->
        <div v-else class="message user-message">
          <div class="message-avatar">
            <img :src="userAvatar" @error="onUserAvatarError" class="avatar-img" alt="You" />
          </div>
          <div class="message-content">
            <div v-if="message.contentType === 'text'" class="text-message">
              {{ message.content }}
            </div>
            <div v-else-if="message.contentType === 'audio'" class="audio-message">
              <div class="audio-player user-audio">
                <SoundOutlined class="audio-icon" />
                <div class="audio-wave">
                  <span v-for="i in 5" :key="i" class="wave-bar"></span>
                </div>
                <span class="duration">{{ formatDuration(message.duration) }}</span>
              </div>
            </div>
            <!-- 时间戳（用户） -->
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input-area">
      <div class="input-controls">
        <button @click="toggleVoiceInput" class="control-btn">
          <AudioOutlined v-if="!isVoiceInput" class="control-icon" />
          <AudioMutedOutlined v-else class="control-icon" />
        </button>
        <button @click="showImagePicker" class="control-btn">
          <PlusOutlined class="control-icon" />
        </button>
      </div>
      
      <div class="input-main">
        <textarea 
          v-if="!isVoiceInput"
          v-model="inputText"
          @keydown.enter.prevent="sendMessage"
          @input="autoResize"
          ref="textInput"
          placeholder="Message Mira..."
          rows="1"
        />
        <div v-else class="voice-input">
          <div class="voice-wave-container">
            <div class="voice-wave" :class="{ recording: isRecording }">
              <span v-for="i in 8" :key="i" class="wave-bar"></span>
            </div>
            <p class="voice-tip">{{ voiceTip }}</p>
          </div>
          <button 
            @touchstart="startRecording" 
            @touchend="stopRecording"
            @touchcancel="cancelRecording"
            class="record-btn"
            :class="{ recording: isRecording }"
          >
            {{ isRecording ? '松开发送' : '按住录音' }}
          </button>
        </div>
      </div>
      
      <button @click="sendMessage" class="send-btn" :disabled="!canSend">
        <SendOutlined class="send-icon" />
      </button>
    </div>
    
    <!-- 图片预览Modal -->
    <Modal
      :open="previewVisible"
      :title="previewTitle"
      :footer="null"
      @cancel="handlePreviewCancel"
      width="80%"
      centered
    >
      <img
        :src="previewImageUrl"
        :alt="previewTitle"
        style="width: 100%; height: auto; border-radius: 8px;"
      />
    </Modal>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick, onUnmounted, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useWebSocket } from '@/composables/useWebSocket'
import { formatTime, formatDuration } from '@/utils/format'
import { useAudioRecorder } from '@/composables/useAudioRecorder'
import { chatAPI } from '@/services/api'
import {
  RobotOutlined,
  UserOutlined,
  SettingOutlined,
  SoundOutlined,
  AudioOutlined,
  AudioMutedOutlined,
  PlusOutlined,
  SendOutlined
} from '@ant-design/icons-vue'
import { Modal } from 'ant-design-vue'

export default {
  name: 'Chat',
  components: {
    RobotOutlined,
    UserOutlined,
    SettingOutlined,
    SoundOutlined,
    AudioOutlined,
    AudioMutedOutlined,
    PlusOutlined,
    SendOutlined
  },
  setup() {
    const chatStore = useChatStore()
    const { connect, /* sendMessage: sendWSMessage, */ isConnected, messages: wsMessages, sessionId, typing, sendActivity } = useWebSocket()
    const { startRecording, stopRecording, cancelRecording, isRecording, recordingTime } = useAudioRecorder()
    
    // 响应式数据
    const messages = ref([
      {
        id: 1,
        sender: 'ai',
        contentType: 'text',
        content: '你好！我是Mira，你的AI朋友。有什么我可以帮助你的吗？',
        timestamp: new Date('2024-01-01T09:30:00')
      }
    ])
    const inputText = ref('')
    const isSending = ref(false)
    const isVoiceInput = ref(false)
    const messagesContainer = ref(null)
    const textInput = ref(null)
    
    // 图片预览状态
    const previewVisible = ref(false)
    const previewImageUrl = ref('')
    const previewTitle = ref('')
    
    // 聊天会话状态
    const currentSessionId = ref(null)
    const isLoading = ref(false)
    const error = ref('')

    // 固定头像（可替换为项目 public 目录下的真实头像）
    const aiAvatar = ref('/images/ai_avatar.jpg')
    const userAvatar = ref('/images/user_avatar.jpg')
    const onAiAvatarError = (e) => { e.target.src = 'https://i.pravatar.cc/100?img=48' }
    const onUserAvatarError = (e) => { e.target.src = 'https://i.pravatar.cc/100?img=1' }
    
    // 计算属性
    const canSend = computed(() => {
      if (isSending.value) return false
      return inputText.value.trim() || isRecording.value
    })
    
    const voiceTip = computed(() => {
      return isRecording.value ? '松开发送' : '按住录音'
    })
    
    // 方法
    const initializeChat = async () => {
      try {
        isLoading.value = true
        error.value = ''

        // 优先获取或创建最近会话，并附带历史
        const latest = await chatAPI.latestOrCreate(true)
        const sessionData = latest?.session || latest?.data?.session || latest
        const history = latest?.messages || latest?.data?.messages || []
        currentSessionId.value = sessionData?.id
        if (!currentSessionId.value) throw new Error('无法获取会话ID')

        // 填充历史
        messages.value = (history || []).map(msg => ({
          id: msg.id,
          sender: msg.sender,
          contentType: msg.content_type,
          content: msg.content,
          text: msg.text,
          alt: msg.alt,
          duration: msg.duration,
          timestamp: new Date(msg.timestamp)
        }))

        // 连接WebSocket
        connect(currentSessionId.value)
      } catch (e) {
        console.error('聊天初始化失败:', e)
        error.value = e?.message || '初始化失败'
        messages.value = [
          {
            id: 1,
            sender: 'ai',
            contentType: 'text',
            content: '你好！我是Mira，你的AI朋友。有什么我可以帮助你的吗？',
            timestamp: new Date()
          }
        ]
      } finally {
        isLoading.value = false
      }
    }
    
    const sendMessage = async () => {
      if (!canSend.value) return
      if (isSending.value) return
      isSending.value = true
      
      try {
        // 生成客户端消息ID用于去重
        const clientMsgId = (typeof crypto !== 'undefined' && crypto.randomUUID) 
          ? crypto.randomUUID() 
          : `cmid_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`

        const messageData = {
          id: clientMsgId,
          sender: 'user',
          timestamp: new Date(),
          contentType: (isVoiceInput.value && isRecording.value) ? 'audio' : 'text',
        }

        if (messageData.contentType === 'audio') {
          messageData.content = await stopRecording()
          messageData.duration = recordingTime.value
        } else {
          messageData.content = inputText.value.trim()
          inputText.value = ''
        }

        // 本地先展示（仅一次）
        messages.value.push(messageData)

        // 仅走 REST，避免与 WS 双通道重复
        if (currentSessionId.value) {
          const payload = {
            content_type: messageData.contentType,
            content: messageData.content,
            text: messageData.text,
            alt: messageData.alt,
            duration: messageData.duration,
            session_id: currentSessionId.value,
            client_msg_id: clientMsgId,
          }
          try {
            await chatAPI.sendMessage(currentSessionId.value, payload)
            // 不再在这里追加 AI 回复，交给 WebSocket 推送，避免重复
          } catch (error) {
            console.error('发送消息到后端失败:', error)
          }
        }

        await nextTick()
        scrollToBottom()
      } finally {
        isSending.value = false
      }
    }
    
    const goToProfile = () => {
      // 导航到个人资料页面
      window.location.href = '/profile'
    }
    
    const goToSettings = () => {
      // 导航到设置页面
      window.location.href = '/settings'
    }
    
    const toggleVoiceInput = () => {
      isVoiceInput.value = !isVoiceInput.value
    }
    
    const showImagePicker = () => {
      // 实现图片选择功能
      console.log('Show image picker')
    }
    
    const previewImage = (imageUrl) => {
      // 实现图片预览功能
      previewImageUrl.value = imageUrl
      previewTitle.value = '图片预览'
      previewVisible.value = true
    }
    
    const handlePreviewCancel = () => {
      previewVisible.value = false
    }

    const handleImageError = (event) => {
      event.target.src = 'https://via.placeholder.com/150'; // 设置一个占位符
    }
    
    const autoResize = () => {
      if (textInput.value) {
        textInput.value.style.height = 'auto'
        textInput.value.style.height = textInput.value.scrollHeight + 'px'
      }
      // 用户在输入，发送活动心跳
      try { sendActivity() } catch (_) {}
    }
    
    const scrollToBottom = () => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }

    // 将 WebSocket 消息映射到本地渲染结构（仅处理 AI 消息，避免用户消息重复）
    const wsCursor = ref(0)
    const seenMessageIds = new Set()
    watch(wsMessages, async (list) => {
      while (wsCursor.value < list.length) {
        const raw = list[wsCursor.value]
        const sender = raw.sender || 'ai'
        if (sender === 'ai') {
          const mappedId = raw.id || `${raw.timestamp || Date.now()}_${(raw.content || '').slice(0, 12)}`
          if (seenMessageIds.has(mappedId)) {
            wsCursor.value += 1
            continue
          }
          const mapped = {
            id: mappedId,
            sender,
            contentType: raw.contentType || raw.content_type || 'text',
            content: raw.content || raw.text || '',
            text: raw.text,
            alt: raw.alt,
            duration: raw.duration,
            timestamp: new Date(raw.timestamp || Date.now())
          }
          messages.value.push(mapped)
          seenMessageIds.add(mappedId)
        }
        wsCursor.value += 1
      }
      await nextTick()
      scrollToBottom()
    }, { deep: true })

    // 打字中状态（AI）
    const isAiTyping = computed(() => {
      try { return !!(typing && typing.value && typing.value.ai) } catch (_) { return false }
    })
    
    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      const hours = date.getHours()
      const minutes = date.getMinutes()
      const ampm = hours >= 12 ? 'PM' : 'AM'
      const displayHours = hours % 12 || 12
      return `${displayHours}:${minutes.toString().padStart(2, '0')} ${ampm}`
    }
    
    const formatDuration = (seconds) => {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    }
    
    // 监听WebSocket消息
    const handleWebSocketMessage = (message) => {
      if (message.sender === 'ai') {
        messages.value.push({
          ...message,
          timestamp: new Date(message.timestamp || new Date())
        })
        
        // 滚动到底部
        nextTick(() => {
          scrollToBottom()
        })
      }
    }
    
    // 生命周期
    onMounted(async () => {
      // 初始化聊天
      await initializeChat()
      
      // 滚动到底部
      scrollToBottom()
      // 页面可见性变化 -> 活动心跳
      const onVis = () => { try { sendActivity() } catch (_) {} }
      document.addEventListener('visibilitychange', onVis)
      window.addEventListener('focus', onVis)
      window.__mira_onVis = onVis
    })
    
    onUnmounted(() => {
      // 清理资源
      try {
        document.removeEventListener('visibilitychange', window.__mira_onVis)
        window.removeEventListener('focus', window.__mira_onVis)
        delete window.__mira_onVis
      } catch (_) {}
    })
    
    const shouldShowImageText = (text) => {
      if (!text) return false
      const t = String(text).trim()
      if (!t) return false
      // 隐藏以“图例”开头的生硬描述
      if (/^图例[:：]/.test(t)) return false
      return true
    }

    const imageTextForDisplay = (text) => {
      if (!text) return ''
      let t = String(text).trim()
      t = t.replace(/^图例[:：]\s*/, '')
      return t
    }

    return {
      messages,
      inputText,
      isSending,
      isVoiceInput,
      isRecording,
      recordingTime,
      messagesContainer,
      textInput,
      canSend,
      voiceTip,
      sendMessage,
      goToProfile,
      goToSettings,
      toggleVoiceInput,
      showImagePicker,
      previewImage,
      previewVisible,
      handlePreviewCancel,
      autoResize,
      formatTime,
      formatDuration,
      handleImageError,
      isLoading,
      error,
      currentSessionId,
      aiAvatar,
      userAvatar,
      onAiAvatarError,
      onUserAvatarError,
      isAiTyping,
      shouldShowImageText,
      imageTextForDisplay
    }
  }
}
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

/* 顶部状态栏 */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px 8px;
  background-color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  color: #000000;
}

.status-icons {
  display: flex;
  gap: 8px;
}

.status-icon {
  font-size: 18px;
  color: #000000;
}

/* 聊天头部 */
.chat-header {
  padding: 0 20px 16px;
  border-bottom: 1px solid #f0f0f0;
  background-color: #ffffff;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #007AFF, #5AC8FA);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-icon {
  font-size: 24px;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-info h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #000000;
}

.ai-status {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #8E8E93;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #f2f2f7;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon {
  font-size: 18px;
  color: #8E8E93;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover .action-icon {
  color: #007AFF;
}

/* 聊天消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  background-color: #ffffff;
}

.typing-indicator {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin: 0 0 12px 44px; /* 对齐AI头像后的位置 */
}
.typing-indicator .dot {
  width: 6px;
  height: 6px;
  background-color: #c7c7cc;
  border-radius: 50%;
  animation: blink 1.2s infinite ease-in-out;
}
.typing-indicator .dot:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator .dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 80%, 100% { opacity: 0.2; }
  40% { opacity: 1; }
}

.message-wrapper {
  margin-bottom: 16px;
}

.message {
  display: flex;
  gap: 8px;
  max-width: 80%;
}

.message.user-message {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f2f2f7;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.message-content {
  flex: 1;
}

.text-message {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 16px;
  line-height: 1.4;
  word-wrap: break-word;
  display: inline-block; /* 关键：使气泡宽度随内容自适应 */
  width: auto;
  max-width: 75%; /* 限制最长行宽，避免过宽影响阅读 */
}

.ai-message .text-message {
  background-color: #f2f2f7;
  color: #000000;
}

.user-message .text-message {
  background-color: #007AFF;
  color: #ffffff;
}

/* 让用户侧文本气泡靠右，但内部文字保持左对齐 */
.user-message .message-content {
  text-align: right;
}
.user-message .text-message {
  text-align: left;
}

.audio-message {
  padding: 12px 16px;
  border-radius: 18px;
  background-color: #f2f2f7;
}

.audio-player {
  display: flex;
  align-items: center;
  gap: 8px;
}

.audio-icon {
  font-size: 16px;
  color: #007AFF;
  display: flex;
  align-items: center;
  justify-content: center;
}

.audio-wave {
  display: flex;
  gap: 2px;
  align-items: center;
}

.wave-bar {
  width: 3px;
  height: 20px;
  background-color: #8E8E93;
  border-radius: 2px;
}

.duration {
  font-size: 14px;
  color: #8E8E93;
  margin-left: 8px;
}

.image-message {
  padding: 12px 16px;
  border-radius: 18px;
  background-color: #f2f2f7;
  max-width: 280px;
}

.image-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.image-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.4;
  color: #000000;
}

.image-message img,
.message-image {
  width: 100%;
  height: auto;
  max-width: 200px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-message img:hover,
.message-image:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.message-time {
  font-size: 12px;
  color: #8E8E93;
  margin-top: 4px;
  text-align: center;
}

.user-message .message-time {
  text-align: right;
}

/* 输入区域 */
.chat-input-area {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 16px 20px;
  background-color: #ffffff;
  border-top: 1px solid #f0f0f0;
}

.input-controls {
  display: flex;
  gap: 8px;
}

.control-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #f2f2f7;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-icon {
  font-size: 18px;
  color: #8E8E93;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-btn:hover .control-icon {
  color: #007AFF;
}

.input-main {
  flex: 1;
}

.input-main textarea {
  width: 100%;
  min-height: 36px;
  max-height: 120px;
  padding: 8px 16px;
  border: 1px solid #e5e5ea;
  border-radius: 18px;
  font-size: 16px;
  line-height: 1.4;
  resize: none;
  outline: none;
  background-color: #f2f2f7;
}

.input-main textarea:focus {
  border-color: #007AFF;
  background-color: #ffffff;
}

.voice-input {
  text-align: center;
}

.voice-wave-container {
  margin-bottom: 12px;
}

.voice-wave {
  display: flex;
  gap: 2px;
  justify-content: center;
  margin-bottom: 8px;
}

.voice-wave.recording .wave-bar {
  animation: wave-animation 0.6s ease-in-out infinite;
}

.wave-bar {
  width: 4px;
  height: 24px;
  background-color: #007AFF;
  border-radius: 2px;
}

.voice-tip {
  font-size: 14px;
  color: #8E8E93;
  margin: 0;
}

.record-btn {
  padding: 8px 16px;
  border: 1px solid #007AFF;
  border-radius: 18px;
  background-color: #007AFF;
  color: #ffffff;
  font-size: 14px;
}

.record-btn.recording {
  background-color: #ff3b30;
  border-color: #ff3b30;
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #007AFF;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
}

.send-btn:disabled {
  background-color: #c7c7cc;
  cursor: not-allowed;
}

.send-icon {
  font-size: 18px;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 动画 */
@keyframes wave-animation {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(1.5); }
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 4px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c7c7cc;
  border-radius: 2px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
