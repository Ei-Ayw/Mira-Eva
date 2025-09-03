import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import router from './router'
import App from './App.vue'

// 引入Ant Design Vue
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'

// 导入全局样式
import './styles/global.css'
import './styles/mobile.css'

// 创建应用实例
const app = createApp(App)

// 使用插件
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(Antd)

// 挂载应用
app.mount('#app')

// 全局监听未授权事件（由 API 动态调用 store）
// 这里确保 store 可被初始化
useAuthStore()
