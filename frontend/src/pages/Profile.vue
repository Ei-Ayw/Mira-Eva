<template>
  <div class="profile-page">
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
      <h1 class="page-title">Profile & Memories</h1>
      <div class="header-actions">
        <button class="documents-btn" @click="goToDocuments">
          <FileTextOutlined class="documents-icon" />
        </button>
        <button class="memories-btn" @click="goToMemories">
          <DatabaseOutlined class="memories-icon" />
        </button>
      </div>
    </div>

    <!-- 个人资料卡片 -->
    <div class="profile-card">
      <div class="profile-avatar">
        <UserOutlined class="avatar-icon" />
      </div>
      <div class="profile-info">
        <h2 class="user-name">{{ displayName }}</h2>
        <p class="profile-description">Mira knows {{ summary.memories.total }} things about you</p>
        <div class="category-counts">
          <span 
            v-for="mc in memoryCountsList" 
            :key="mc.type"
            class="count-badge"
          >
            <BookOutlined v-if="mc.type === 'fact'" class="badge-icon" />
            <CalendarOutlined v-else-if="mc.type === 'event'" class="badge-icon" />
            <StarOutlined v-else-if="mc.type === 'preference'" class="badge-icon" />
            <BookOutlined v-else class="badge-icon" />
            {{ mc.count }} {{ mc.type }}
          </span>
        </div>
      </div>
    </div>

    <!-- 内容分类（按记忆类型） -->
    <div class="content-sections">
      <div 
        v-for="mc in memoryCountsList" 
        :key="mc.type"
        class="section-item"
      >
        <div class="section-dot"></div>
        <div class="section-content">
          <span class="section-title">{{ mc.type }}</span>
          <span class="section-count">{{ mc.count }}</span>
        </div>
        <RightOutlined class="section-arrow" />
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <div class="stats-card">
        <div class="stats-icon">
          <AimOutlined />
        </div>
        <div class="stats-content">
          <h3 class="stats-title">Memories</h3>
          <p class="stats-value">{{ summary.memories.total }}</p>
          <p class="stats-description">Total memories stored</p>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">
          <MessageOutlined />
        </div>
        <div class="stats-content">
          <h3 class="stats-title">Messages</h3>
          <p class="stats-value">{{ summary.chat.total_messages }}</p>
          <p class="stats-description">Sessions: {{ summary.chat.total_sessions }} · AI: {{ summary.chat.ai_messages }} / U: {{ summary.chat.user_messages }}</p>
        </div>
      </div>
    </div>

    <!-- 最近会话与消息 -->
    <div class="stats-section" v-if="summary.chat.recent">
      <div class="stats-card" style="grid-column: 1 / -1; text-align: left;">
        <h3 class="stats-title">Recent Conversation</h3>
        <div v-if="summary.chat.recent.messages && summary.chat.recent.messages.length">
          <div v-for="m in summary.chat.recent.messages" :key="m.id" style="margin: 8px 0;">
            <strong style="color:#007AFF">{{ m.sender === 'ai' ? 'Mira' : 'You' }}:</strong>
            <span>{{ m.content }}</span>
          </div>
        </div>
        <div v-else style="color:#8E8E93">No recent messages</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { profileAPI } from '@/services/api'
import {
  LeftOutlined,
  RightOutlined,
  UserOutlined,
  BookOutlined,
  CalendarOutlined,
  StarOutlined,
  AimOutlined,
  MessageOutlined,
  FileTextOutlined,
  DatabaseOutlined
} from '@ant-design/icons-vue'

export default {
  name: 'Profile',
  components: {
    LeftOutlined,
    RightOutlined,
    UserOutlined,
    BookOutlined,
    CalendarOutlined,
    StarOutlined,
    AimOutlined,
    MessageOutlined,
    FileTextOutlined,
    DatabaseOutlined
  },
  setup() {
    const router = useRouter()
    const isLoading = ref(false)
    const error = ref('')

    const summary = ref({
      user: {},
      profile: {},
      memories: { total: 0, by_type: {} },
      chat: { total_sessions: 0, active_sessions: 0, total_messages: 0, user_messages: 0, ai_messages: 0, recent: null }
    })

    const memoryCountsList = computed(() => {
      const bt = summary.value.memories?.by_type || {}
      return Object.keys(bt).map(k => ({ type: k, count: bt[k] }))
    })

    const displayName = computed(() => {
      const u = summary.value.user || {}
      const p = summary.value.profile || {}
      return p.full_name || [u.first_name, u.last_name].filter(Boolean).join(' ') || u.username || 'User'
    })

    const goBack = () => {
      window.history.back()
    }

    const goToDocuments = () => {
      router.push('/documents')
    }

    const goToMemories = () => {
      router.push('/memories')
    }

    const loadProfileData = async () => {
      try {
        isLoading.value = true
        error.value = ''
        const resp = await profileAPI.getProfileSummary()
        const data = resp?.data ?? resp
        if (!data) throw new Error('空数据')
        summary.value = {
          user: data.user || {},
          profile: data.profile || {},
          memories: data.memories || { total: 0, by_type: {} },
          chat: data.chat || { total_sessions: 0, active_sessions: 0, total_messages: 0, user_messages: 0, ai_messages: 0, recent: null }
        }
      } catch (e) {
        error.value = e?.message || '加载失败'
      } finally {
        isLoading.value = false
      }
    }

    onMounted(loadProfileData)

    return { isLoading, error, summary, memoryCountsList, displayName, goBack, goToDocuments, goToMemories }
  }
}
</script>

<style scoped>
.profile-page {
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
  flex: 1;
}

.header-actions {
  display: flex;
  gap: 12px;
  margin-left: 16px;
}

.documents-btn,
.memories-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #007AFF;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.documents-btn:hover,
.memories-btn:hover {
  background-color: #0056CC;
  transform: translateY(-2px);
}

.documents-icon,
.memories-icon {
  font-size: 18px;
  color: #FFFFFF;
}

/* 个人资料卡片 */
.profile-card {
  margin: 16px;
  padding: 24px;
  background-color: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #F0F0F0;
  text-align: center;
}

.profile-avatar {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
}

.avatar-icon {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: #F2F2F7;
  border: 2px solid #E5E5EA;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #8E8E93;
  padding: 16px;
}

.profile-info {
  text-align: center;
}

.user-name {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 700;
  color: #000000;
}

.profile-description {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: #8E8E93;
  line-height: 1.4;
}

.category-counts {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.count-badge {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  color: #FFFFFF;
  background-color: #007AFF;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.count-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
}

.badge-icon {
  font-size: 12px;
}

/* 内容分类 */
.content-sections {
  margin: 0 16px 24px;
}

.section-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background-color: #FFFFFF;
  border-radius: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #F0F0F0;
}

.section-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  background-color: #F8F9FA;
}

.section-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  background-color: #007AFF;
}

.section-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #000000;
}

.section-count {
  font-size: 14px;
  font-weight: 700;
  color: #007AFF;
  background: rgba(0, 122, 255, 0.1);
  padding: 3px 10px;
  border-radius: 10px;
}

.section-arrow {
  color: #C7C7CC;
  font-size: 18px;
  font-weight: 300;
  transition: all 0.3s ease;
}

.section-item:hover .section-arrow {
  color: #007AFF;
  transform: translateX(4px);
}

/* 统计卡片 */
.stats-section {
  margin: 0 16px 24px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stats-card {
  padding: 20px;
  background-color: #FFFFFF;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #F0F0F0;
  transition: all 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stats-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #F2F2F7;
  border: 2px solid #E5E5EA;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  font-size: 20px;
  color: #8E8E93;
}

.stats-title {
  margin: 0 0 6px 0;
  font-size: 14px;
  font-weight: 600;
  color: #8E8E93;
}

.stats-value {
  margin: 0 0 6px 0;
  font-size: 24px;
  font-weight: 800;
  color: #007AFF;
}

.stats-description {
  margin: 0;
  font-size: 12px;
  color: #8E8E93;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .profile-card,
  .content-sections,
  .stats-section {
    margin: 20px 16px;
  }
  
  .profile-card {
    padding: 24px;
  }
  
  .section-item {
    padding: 20px;
  }
  
  .stats-section {
    grid-template-columns: 1fr;
  }
  
  .user-name {
    font-size: 24px;
  }
  
  .section-title {
    font-size: 16px;
  }
  
  .category-counts {
    gap: 8px;
  }
  
  .count-badge {
    padding: 6px 12px;
    font-size: 12px;
  }
}
</style>
