<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-header">
        <h1>Mira</h1>
        <p>加入数字孪生朋友的世界</p>
      </div>
      
      <div class="register-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            id="username"
            v-model="username" 
            type="text" 
            placeholder="请输入用户名"
            @keydown.enter="handleRegister"
          />
        </div>
        
        <div class="form-group">
          <label for="email">邮箱</label>
          <input 
            id="email"
            v-model="email" 
            type="email" 
            placeholder="请输入邮箱"
            @keydown.enter="handleRegister"
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            id="password"
            v-model="password" 
            type="password" 
            placeholder="请输入密码"
            @keydown.enter="handleRegister"
          />
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input 
            id="confirmPassword"
            v-model="confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            @keydown.enter="handleRegister"
          />
        </div>
        
        <button 
          @click="handleRegister" 
          class="register-btn"
          :disabled="!canRegister || isLoading"
        >
          {{ isLoading ? '注册中...' : '注册' }}
        </button>
        
        <div class="form-footer">
          <span>已有账号？</span>
          <router-link to="/login" class="link">立即登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const username = ref('')
    const email = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const isLoading = ref(false)
    
    const canRegister = computed(() => {
      return username.value.trim() && 
             email.value.trim() && 
             password.value.trim() && 
             confirmPassword.value.trim() &&
             password.value === confirmPassword.value
    })
    
    const handleRegister = async () => {
      if (!canRegister.value || isLoading.value) return
      
      try {
        isLoading.value = true
        
        // 模拟注册逻辑
        if (password.value !== confirmPassword.value) {
          alert('两次输入的密码不一致')
          return
        }
        
        // 模拟注册成功
        alert('注册成功！请使用新账号登录')
        
        // 跳转到登录页面
        router.push('/login')
      } catch (error) {
        console.error('注册失败:', error)
        alert('注册失败，请重试')
      } finally {
        isLoading.value = false
      }
    }
    
    return {
      username,
      email,
      password,
      confirmPassword,
      isLoading,
      canRegister,
      handleRegister
    }
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h1 {
  font-size: 48px;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.register-header p {
  margin: 10px 0 0 0;
  color: #666;
  font-size: 16px;
}

.register-form {
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
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.form-group input {
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 10px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.register-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.register-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.form-footer .link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  margin-left: 5px;
}

.form-footer .link:hover {
  text-decoration: underline;
}

/* 移动端适配 */
@media (max-width: 480px) {
  .register-container {
    padding: 30px 20px;
    margin: 20px;
  }
  
  .register-header h1 {
    font-size: 36px;
  }
}
</style>
