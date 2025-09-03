import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Chat from '@/pages/Chat.vue'
import Profile from '@/pages/Profile.vue'
import Settings from '@/pages/Settings.vue'
import Demo from '@/pages/Demo.vue'
import Login from '@/pages/Login.vue'

const routes = [
  {
    path: '/',
    redirect: '/chat'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true }
  },
  {
    path: '/demo',
    name: 'Demo',
    component: Demo,
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    auth.promptLoginIfNeeded('访问该页面需要登录')
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if (to.path === '/login' && auth.isAuthenticated) {
    next('/chat')
  } else {
    next()
  }
})

export default router
