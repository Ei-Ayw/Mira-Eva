import { ref, computed } from 'vue'

// 认证状态
const isAuthenticated = ref(false)
const currentUser = ref(null)
const authToken = ref(localStorage.getItem('auth_token') || null)

// API基础URL
const API_BASE_URL = 'http://localhost:8000/api'

// 认证方法
export function useAuth() {
  // 登录
  const login = async (username, password) => {
    try {
      // 调用真实的JWT API
      const response = await fetch(`${API_BASE_URL}/token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '登录失败')
      }

      const data = await response.json()
      const { access, refresh } = data

      // 保存JWT token
      authToken.value = access
      currentUser.value = { username, id: 1 } // 简化用户信息
      isAuthenticated.value = true
      
      // 保存到本地存储
      localStorage.setItem('auth_token', access)
      localStorage.setItem('refresh_token', refresh)
      localStorage.setItem('user', JSON.stringify({ username, id: 1 }))
      
      console.log('JWT登录成功:', { username, access: access.substring(0, 20) + '...' })
      return { success: true, user: { username, id: 1 } }
      
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, error: error.message }
    }
  }
  
  // 登出
  const logout = () => {
    authToken.value = null
    currentUser.value = null
    isAuthenticated.value = false
    
    // 清除本地存储
    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    
    console.log('已登出')
  }
  
  // 检查认证状态
  const checkAuth = () => {
    const token = localStorage.getItem('auth_token')
    const user = localStorage.getItem('user')
    
    if (token && user) {
      try {
        // 验证token格式（JWT token通常以eyJ开头）
        if (token.startsWith('eyJ')) {
          authToken.value = token
          currentUser.value = JSON.parse(user)
          isAuthenticated.value = true
          return true
        } else {
          // 清除无效的token
          logout()
          return false
        }
      } catch (error) {
        console.error('解析用户数据失败:', error)
        logout()
        return false
      }
    }
    return false
  }
  
  // 获取认证头
  const getAuthHeaders = (contentType = null) => {
    const headers = {}
    
    if (authToken.value) {
      headers['Authorization'] = `Bearer ${authToken.value}`
    }
    
    // 只有在明确指定时才设置 Content-Type
    // 对于文件上传，让浏览器自动设置 multipart/form-data
    if (contentType) {
      headers['Content-Type'] = contentType
    }
    
    return headers
  }
  
  // 刷新token
  const refreshToken = async () => {
    try {
      const refresh = localStorage.getItem('refresh_token')
      if (!refresh) {
        throw new Error('没有刷新token')
      }

      const response = await fetch(`${API_BASE_URL}/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh })
      })

      if (!response.ok) {
        throw new Error('刷新token失败')
      }

      const data = await response.json()
      const { access } = data

      // 更新token
      authToken.value = access
      localStorage.setItem('auth_token', access)
      
      console.log('Token已刷新')
      return true
      
    } catch (error) {
      console.error('刷新token失败:', error)
      logout()
      return false
    }
  }
  
  // 计算属性
  const userDisplayName = computed(() => {
    if (currentUser.value) {
      return currentUser.value.username || '未登录'
    }
    return '未登录'
  })
  
  // 初始化时检查认证状态
  if (!isAuthenticated.value) {
    checkAuth()
  }
  
  return {
    // 状态
    isAuthenticated,
    currentUser,
    authToken,
    userDisplayName,
    
    // 方法
    login,
    logout,
    checkAuth,
    getAuthHeaders,
    refreshToken
  }
}
