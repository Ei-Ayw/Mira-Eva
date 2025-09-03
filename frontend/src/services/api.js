// 基础配置
const API_BASE_URL = 'http://localhost:8000/api'
const WS_BASE_URL = 'ws://localhost:8000/ws'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
    this.wsBaseURL = WS_BASE_URL
  }

  getAuthHeaders() {
    const token = localStorage.getItem('auth_token')
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers['Authorization'] = `Bearer ${token}`
    return headers
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      method: 'GET',
      headers: this.getAuthHeaders(),
      ...options,
    }
    if (options.headers) config.headers = { ...config.headers, ...options.headers }
    try {
      const res = await fetch(url, config)
      if (!res.ok) {
        if (res.status === 401 || res.status === 403) {
          try {
            const { useAuthStore } = await import('@/stores/auth')
            useAuthStore().handleUnauthorized('登录状态失效或无权限访问')
          } catch (_) {}
        }
        throw new Error(`HTTP ${res.status}`)
      }
      return await res.json()
    } catch (e) {
      console.error('API请求失败:', e)
      throw e
    }
  }

  async get(endpoint) { return this.request(endpoint) }
  async post(endpoint, data) { return this.request(endpoint, { method: 'POST', body: JSON.stringify(data) }) }
  async put(endpoint, data) { return this.request(endpoint, { method: 'PUT', body: JSON.stringify(data) }) }
  async delete(endpoint) { return this.request(endpoint, { method: 'DELETE' }) }

  async uploadFile(endpoint, file, additional = {}) {
    const form = new FormData()
    if (file) form.append('file', file)
    Object.keys(additional || {}).forEach(k => form.append(k, additional[k]))
    const token = localStorage.getItem('auth_token')
    const url = `${this.baseURL}${endpoint}`
    const res = await fetch(url, { method: 'POST', headers: { 'Authorization': token ? `Bearer ${token}` : '' }, body: form })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  }

  getWebSocketURL(sessionId) { return `${this.wsBaseURL}/chat/${sessionId}/` }
}

const apiService = new ApiService()

export const chatAPI = {
  async latestOrCreate(withMessages = true) {
    const qs = withMessages ? '?messages=1' : ''
    return apiService.get(`/chat/sessions/latest_or_create/${qs}`)
  },
  async getChatHistory(sessionId) {
    return apiService.get(`/chat/messages/?session_id=${sessionId}`)
  },
  async sendMessage(sessionId, messageData) {
    return apiService.post('/chat/messages/', { session_id: sessionId, ...messageData })
  },
  async uploadImage(sessionId, imageFile, altText = '') {
    return apiService.uploadFile('/chat/upload/', imageFile, { type: 'image', session_id: sessionId, alt_text: altText })
  },
  async uploadAudio(sessionId, audioFile, duration = 0) {
    return apiService.uploadFile('/chat/upload/', audioFile, { type: 'audio', session_id: sessionId, duration })
  },
}

export const profileAPI = {
  async getProfileSummary() { return apiService.get('/profile/profile/') },
  async updateProfile(data) { return apiService.put('/profile/profile/', data) },
  async updateAvatar(file) { return apiService.uploadFile('/profile/profile/update_avatar/', file) },
}

export const settingsAPI = {
  async getUserSettings() { return apiService.get('/settings/settings/') },
  async updateUserSettings(data) { return apiService.put('/settings/settings/', data) },
}

export { apiService }


