<template>
  <div class="settings-page">
    <!-- 顶部状态栏 -->
    <div class="status-bar">
      <span class="time">9:41</span>
      <div class="status-icons">
        <span class="status-icon">⋮</span>
      </div>
    </div>

    <!-- 页面头部 -->
    <div class="page-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
      </button>
      <h1 class="page-title">Settings & Skills</h1>
    </div>

    <!-- 自定义Mira卡片 -->
    <div class="customize-card">
      <div class="card-icon">
        <SettingOutlined />
      </div>
      <div class="card-content">
        <h2 class="card-title">Customize Your Mira</h2>
        <p class="card-description">Adjust these settings to make Mira more suited to your preferences</p>
      </div>
    </div>

    <!-- Mira的个性设置 -->
    <div class="settings-section">
      <h3 class="section-title">MIRA'S PERSONALITY</h3>
      
      <div class="setting-item">
        <div class="setting-icon">
          <StarOutlined />
        </div>
        <div class="setting-content">
          <div class="setting-header">
            <span class="setting-label">Enthusiasm</span>
            <span class="setting-value">{{ enthusiasm }}%</span>
          </div>
          <p class="setting-description">How energetic and excited Mira sounds</p>
          <div class="slider-container">
            <span class="slider-label">Low</span>
            <div class="custom-slider">
              <input 
                type="range" 
                v-model="enthusiasm" 
                min="0" 
                max="100" 
                class="slider"
                @input="updateEnthusiasm"
              />
              <div class="slider-track">
                <div class="slider-fill" :style="{ width: enthusiasm + '%' }"></div>
              </div>
            </div>
            <span class="slider-label">High</span>
          </div>
        </div>
      </div>
      
      <div class="setting-item">
        <div class="setting-icon">
          <MessageOutlined />
        </div>
        <div class="setting-content">
          <div class="setting-header">
            <span class="setting-label">Talkativeness</span>
            <span class="setting-value">{{ talkativeness }}%</span>
          </div>
          <p class="setting-description">How much Mira likes to chat and elaborate</p>
          <div class="slider-container">
            <span class="slider-label">Low</span>
            <div class="custom-slider">
              <input 
                type="range" 
                v-model="talkativeness" 
                min="0" 
                max="100" 
                class="slider"
                @input="updateTalkativeness"
              />
              <div class="slider-track">
                <div class="slider-fill" :style="{ width: talkativeness + '%' }"></div>
              </div>
            </div>
            <span class="slider-label">High</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 通知设置 -->
    <div class="settings-section">
      <h3 class="section-title">NOTIFICATION SETTINGS</h3>
      
      <div class="setting-item">
        <div class="setting-icon">
          <BellOutlined />
        </div>
        <div class="setting-content">
          <div class="setting-header">
            <span class="setting-label">Active Messages</span>
            <label class="toggle-switch">
              <input 
                type="checkbox" 
                v-model="activeMessages" 
                @change="updateNotificationSettings"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <p class="setting-description">Receive proactive messages from Mira</p>
        </div>
      </div>
    </div>

    <!-- 技能设置 -->
    <div class="settings-section">
      <h3 class="section-title">SKILLS</h3>
      
      <div class="setting-item">
        <div class="setting-icon">
          <PictureOutlined />
        </div>
        <div class="setting-content">
          <div class="setting-header">
            <span class="setting-label">Generate Images</span>
            <label class="toggle-switch">
              <input 
                type="checkbox" 
                v-model="generateImages" 
                @change="updateFeatureSettings"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <p class="setting-description">Allow Mira to create and share images</p>
        </div>
      </div>
      
      <div class="setting-item">
        <div class="setting-icon">
          <AudioOutlined />
        </div>
        <div class="setting-content">
          <div class="setting-header">
            <span class="setting-label">Send Voice Messages</span>
            <label class="toggle-switch">
              <input 
                type="checkbox" 
                v-model="sendVoiceMessages" 
                @change="updateFeatureSettings"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <p class="setting-description">Enable Mira to send voice messages</p>
        </div>
      </div>
    </div>

    <!-- 关于和反馈 -->
    <div class="settings-section">
      <h3 class="section-title">ABOUT & FEEDBACK</h3>
      
      <div class="setting-item clickable" @click="showAbout">
        <div class="setting-icon">
          <InfoCircleOutlined />
        </div>
        <div class="setting-content">
          <div class="setting-header">
            <span class="setting-label">About Mira</span>
            <span class="chevron">→</span>
          </div>
          <p class="setting-description">Version 1.0.0</p>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <button class="action-btn primary" @click="resetSettings" :disabled="isLoading">
        <ReloadOutlined class="btn-icon" />
        Reset to Default
      </button>
      <button class="action-btn secondary" @click="exportSettings" :disabled="isLoading">
        <ExportOutlined class="btn-icon" />
        Export Settings
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { settingsAPI } from '@/services/api'
import {
  LeftOutlined,
  RightOutlined,
  SettingOutlined,
  StarOutlined,
  MessageOutlined,
  BellOutlined,
  PictureOutlined,
  AudioOutlined,
  InfoCircleOutlined,
  ReloadOutlined,
  ExportOutlined
} from '@ant-design/icons-vue'

export default {
  name: 'Settings',
  components: {
    LeftOutlined,
    RightOutlined,
    SettingOutlined,
    StarOutlined,
    MessageOutlined,
    BellOutlined,
    PictureOutlined,
    AudioOutlined,
    InfoCircleOutlined,
    ReloadOutlined,
    ExportOutlined
  },
  setup() {
    // 响应式数据
    const enthusiasm = ref(70)
    const talkativeness = ref(60)
    const formality = ref(50)
    const creativity = ref(80)
    
    // 通知设置
    const activeMessages = ref(true)
    const memoryUpdates = ref(true)
    const systemNotifications = ref(true)
    const emailNotifications = ref(false)
    
    // 功能设置
    const generateImages = ref(true)
    const sendVoiceMessages = ref(true)
    const autoSaveChat = ref(true)
    const privacyMode = ref(false)
    
    // 界面设置
    const theme = ref('auto')
    const language = ref('zh-cn')
    
    const isLoading = ref(false)
    const error = ref(null)
    
    // 方法
    const goBack = () => {
      window.history.back()
    }
    
    const updateEnthusiasm = async (value) => {
      enthusiasm.value = value
      await updateAIPersonality()
    }
    
    const updateTalkativeness = async (value) => {
      talkativeness.value = value
      await updateAIPersonality()
    }
    
    const updateAIPersonality = async () => {
      try {
        await settingsAPI.updateAIPersonality({
          enthusiasm: enthusiasm.value,
          talkativeness: talkativeness.value,
          formality: formality.value,
          creativity: creativity.value
        })
        console.log('AI个性设置更新成功')
      } catch (err) {
        console.error('更新AI个性设置失败:', err)
      }
    }
    
    const updateNotificationSettings = async () => {
      try {
        await settingsAPI.updateNotificationSettings({
          active_messages: activeMessages.value,
          memory_updates: memoryUpdates.value,
          system_notifications: systemNotifications.value,
          email_notifications: emailNotifications.value
        })
        console.log('通知设置更新成功')
      } catch (err) {
        console.error('更新通知设置失败:', err)
      }
    }
    
    const updateFeatureSettings = async () => {
      try {
        await settingsAPI.updateFeatureSettings({
          generate_images: generateImages.value,
          send_voice_messages: sendVoiceMessages.value,
          auto_save_chat: autoSaveChat.value,
          privacy_mode: privacyMode.value
        })
        console.log('功能设置更新成功')
      } catch (err) {
        console.error('更新功能设置失败:', err)
      }
    }
    
    const updateInterfaceSettings = async () => {
      try {
        await settingsAPI.updateInterfaceSettings({
          theme: theme.value,
          language: language.value
        })
        console.log('界面设置更新成功')
      } catch (err) {
        console.error('更新界面设置失败:', err)
      }
    }
    
    const resetSettings = async () => {
      try {
        isLoading.value = true
        const data = await settingsAPI.resetToDefault()
        
        // 更新本地状态
        enthusiasm.value = data.enthusiasm
        talkativeness.value = data.talkativeness
        formality.value = data.formality
        creativity.value = data.creativity
        
        activeMessages.value = data.active_messages
        memoryUpdates.value = data.memory_updates
        systemNotifications.value = data.system_notifications
        emailNotifications.value = data.email_notifications
        
        generateImages.value = data.generate_images
        sendVoiceMessages.value = data.send_voice_messages
        autoSaveChat.value = data.auto_save_chat
        privacyMode.value = data.privacy_mode
        
        theme.value = data.theme
        language.value = data.language
        
        console.log('设置重置成功')
      } catch (err) {
        console.error('重置设置失败:', err)
        error.value = '重置设置失败'
      } finally {
        isLoading.value = false
      }
    }
    
    const exportSettings = async () => {
      try {
        const data = await settingsAPI.exportSettings()
        console.log('设置导出成功:', data)
        
        // 创建下载链接
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `mira-settings-${new Date().toISOString().split('T')[0]}.json`
        a.click()
        URL.revokeObjectURL(url)
      } catch (err) {
        console.error('导出设置失败:', err)
        error.value = '导出设置失败'
      }
    }
    
    const showAbout = () => {
      console.log('显示关于信息')
    }
    
    const loadSettings = async () => {
      try {
        isLoading.value = true
        error.value = null
        
        // 尝试从API获取设置
        const [aiPersonality, notifications, features, interfaceSettings] = await Promise.all([
          settingsAPI.getAIPersonality(),
          settingsAPI.getNotificationSettings(),
          settingsAPI.getFeatureSettings(),
          settingsAPI.getInterfaceSettings()
        ])
        
        // 更新本地状态
        enthusiasm.value = aiPersonality.enthusiasm
        talkativeness.value = aiPersonality.talkativeness
        formality.value = aiPersonality.formality
        creativity.value = aiPersonality.creativity
        
        activeMessages.value = notifications.active_messages
        memoryUpdates.value = notifications.memory_updates
        systemNotifications.value = notifications.system_notifications
        emailNotifications.value = notifications.email_notifications
        
        generateImages.value = features.generate_images
        sendVoiceMessages.value = features.send_voice_messages
        autoSaveChat.value = features.auto_save_chat
        privacyMode.value = features.privacy_mode
        
        theme.value = interfaceSettings.theme
        language.value = interfaceSettings.language
        
        console.log('设置加载成功')
      } catch (err) {
        console.error('加载设置失败:', err)
        error.value = '加载设置失败，使用默认值'
        
        // 使用默认值作为后备
        enthusiasm.value = 70
        talkativeness.value = 60
        formality.value = 50
        creativity.value = 80
        
        activeMessages.value = true
        memoryUpdates.value = true
        systemNotifications.value = true
        emailNotifications.value = false
        
        generateImages.value = true
        sendVoiceMessages.value = true
        autoSaveChat.value = true
        privacyMode.value = false
        
        theme.value = 'auto'
        language.value = 'zh-cn'
      } finally {
        isLoading.value = false
      }
    }
    
    // 生命周期
    onMounted(() => {
      loadSettings()
    })
    
    return {
      enthusiasm,
      talkativeness,
      formality,
      creativity,
      activeMessages,
      memoryUpdates,
      systemNotifications,
      emailNotifications,
      generateImages,
      sendVoiceMessages,
      autoSaveChat,
      privacyMode,
      theme,
      language,
      isLoading,
      error,
      goBack,
      updateEnthusiasm,
      updateTalkativeness,
      updateAIPersonality,
      updateNotificationSettings,
      updateFeatureSettings,
      updateInterfaceSettings,
      resetSettings,
      exportSettings,
      showAbout
    }
  }
}
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background-color: #FFFFFF;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

/* 顶部状态栏 */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px 8px;
  background-color: #FFFFFF;
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

/* 页面头部 */
.page-header {
  display: flex;
  align-items: center;
  padding: 20px;
  background-color: #FFFFFF;
  border-bottom: 1px solid #F0F0F0;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #F2F2F7;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background-color: #E5E5EA;
  transform: translateY(-2px);
}

.back-icon {
  font-size: 18px;
  color: #007AFF;
  font-weight: bold;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #000000;
}

/* 自定义Mira卡片 */
.customize-card {
  margin: 16px;
  padding: 24px;
  background-color: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #F0F0F0;
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #F2F2F7;
  border: 2px solid #E5E5EA;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 20px;
  color: #8E8E93;
}

.card-content {
  flex: 1;
}

.card-title {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 700;
  color: #000000;
}

.card-description {
  margin: 0;
  font-size: 14px;
  color: #8E8E93;
  line-height: 1.4;
}

/* 设置区域 */
.settings-section {
  margin: 0 16px 20px;
  background-color: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #F0F0F0;
  overflow: hidden;
}

.section-title {
  margin: 0;
  padding: 16px 20px 12px;
  font-size: 12px;
  font-weight: 700;
  color: #8E8E93;
  text-transform: uppercase;
  letter-spacing: 1px;
  background-color: #F8F9FA;
  border-bottom: 1px solid #F0F0F0;
}

.setting-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  border-bottom: 1px solid #F0F0F0;
  transition: all 0.3s ease;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item.clickable {
  cursor: pointer;
}

.setting-item.clickable:hover {
  background-color: #F8F9FA;
}

.setting-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #F2F2F7;
  border: 2px solid #E5E5EA;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 16px;
  color: #8E8E93;
}

.setting-content {
  flex: 1;
}

.setting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.setting-label {
  font-size: 16px;
  font-weight: 600;
  color: #000000;
}

.setting-value {
  font-size: 14px;
  font-weight: 700;
  color: #007AFF;
  background: rgba(0, 122, 255, 0.1);
  padding: 3px 10px;
  border-radius: 10px;
}

.setting-description {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #8E8E93;
  line-height: 1.4;
}

/* 滑块容器 */
.slider-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.slider-label {
  font-size: 12px;
  color: #8E8E93;
  min-width: 25px;
  font-weight: 500;
}

.custom-slider {
  flex: 1;
  position: relative;
}

.slider {
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: transparent;
  outline: none;
  -webkit-appearance: none;
  position: relative;
  z-index: 2;
}

.slider-track {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: #E5E5EA;
  border-radius: 2px;
  overflow: hidden;
}

.slider-fill {
  height: 100%;
  background-color: #007AFF;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #FFFFFF;
  border: 2px solid #007AFF;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* 开关样式 */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 28px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #E5E5EA;
  transition: 0.3s;
  border-radius: 28px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 22px;
  width: 22px;
  left: 3px;
  bottom: 3px;
  background: #FFFFFF;
  transition: 0.3s;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

input:checked + .toggle-slider {
  background-color: #007AFF;
}

input:checked + .toggle-slider:before {
  transform: translateX(20px);
}

/* 箭头图标 */
.chevron {
  color: #C7C7CC;
  font-size: 16px;
  font-weight: 300;
  transition: all 0.3s ease;
}

.setting-item.clickable:hover .chevron {
  color: #007AFF;
  transform: translateX(4px);
}

/* 快速操作 */
.quick-actions {
  margin: 0 16px 24px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.action-btn {
  padding: 14px 16px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.action-btn.primary {
  background-color: #007AFF;
  color: #FFFFFF;
}

.action-btn.secondary {
  background-color: #FFFFFF;
  color: #007AFF;
  border: 2px solid rgba(0, 122, 255, 0.2);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.action-btn.primary:hover {
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
}

.action-btn.secondary:hover {
  background-color: #F8F9FA;
  border-color: rgba(0, 122, 255, 0.3);
}

.btn-icon {
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .customize-card,
  .settings-section,
  .quick-actions {
    margin: 20px 16px;
  }
  
  .customize-card {
    padding: 24px;
    flex-direction: column;
    text-align: center;
  }
  
  .setting-item {
    padding: 20px;
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
  
  .card-title {
    font-size: 20px;
  }
  
  .setting-label {
    font-size: 16px;
  }
  
  .slider-container {
    gap: 12px;
  }
  
  .slider-label {
    min-width: 25px;
    font-size: 12px;
  }
}
</style>
