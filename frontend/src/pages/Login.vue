<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1 class="app-title">Mira-Eva</h1>
        <p class="app-subtitle">你的AI朋友</p>
      </div>
      
      <div class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            id="username"
            v-model="username" 
            type="text" 
            placeholder="请输入用户名"
            @keyup.enter="handleLogin"
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            id="password"
            v-model="password" 
            type="password" 
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
          />
        </div>
        
        <button 
          class="login-btn" 
          @click="handleLogin"
          :disabled="isLoading"
        >
          {{ isLoading ? '登录中...' : '登录' }}
        </button>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div class="demo-info">
          <p><strong>演示账号:</strong></p>
          <p>用户名: admin</p>
          <p>密码: admin123</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const { login } = useAuth()
    const router = useRouter()
    
    const username = ref('')
    const password = ref('')
    const isLoading = ref(false)
    const error = ref('')
    
    const handleLogin = async () => {
      if (!username.value || !password.value) {
        error.value = '请输入用户名和密码'
        return
      }
      
      try {
        isLoading.value = true
        error.value = ''
        
        const result = await login(username.value, password.value)
        
        if (result.success) {
          console.log('登录成功，跳转到聊天页面')
          router.push('/chat')
        } else {
          error.value = result.error || '登录失败'
        }
      } catch (err) {
        error.value = err.message || '登录失败'
      } finally {
        isLoading.value = false
      }
    }
    
    return {
      username,
      password,
      isLoading,
      error,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-container {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.app-title {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px 0;
}

.app-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.form-group input {
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.login-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 20px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
}

.demo-info {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 12px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.demo-info p {
  margin: 4px 0;
}

.demo-info strong {
  color: #333;
}
</style>
