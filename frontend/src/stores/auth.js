import { defineStore } from 'pinia'
import { Modal } from 'ant-design-vue'
import router from '@/router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('auth_token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    lastAuthModalAt: 0,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token && state.token.startsWith('eyJ'),
  },
  actions: {
    setToken(token, user = null) {
      this.token = token || ''
      if (token) localStorage.setItem('auth_token', token)
      else localStorage.removeItem('auth_token')
      if (user) {
        this.user = user
        localStorage.setItem('user', JSON.stringify(user))
      }
    },
    clearAuth() {
      this.token = ''
      this.user = null
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
    },
    async promptLoginIfNeeded(message = '登录已过期，请重新登录') {
      const now = Date.now()
      if (now - this.lastAuthModalAt < 1500) return
      this.lastAuthModalAt = now
      this.clearAuth()
      await new Promise((resolve) => {
        Modal.warning({
          title: '需要登录',
          content: message,
          okText: '去登录',
          onOk: () => resolve(),
        })
      })
      if (router.currentRoute.value.path !== '/login') {
        router.push({ path: '/login', query: { redirect: router.currentRoute.value.fullPath } })
      }
    },
    handleUnauthorized(message) {
      this.promptLoginIfNeeded(message)
    }
  }
})


