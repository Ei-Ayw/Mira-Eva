<template>
  <div class="demo-page">
    <!-- 顶部状态栏 -->
    <div class="status-bar">
      <span class="time">9:41</span>
      <div class="status-icons">
        <a-button type="text" class="status-icon-btn">
          <template #icon><EllipsisOutlined /></template>
        </a-button>
      </div>
    </div>

    <!-- 页面头部 -->
    <a-card class="page-header" :bordered="false" size="small">
      <div class="header-content">
        <a-button 
          type="text" 
          shape="circle" 
          class="back-btn"
          @click="goBack"
        >
          <template #icon><LeftOutlined /></template>
        </a-button>
        <h1 class="page-title">Ant Design Vue 组件演示</h1>
      </div>
    </a-card>

    <!-- 组件展示区域 -->
    <div class="demo-content">
      <!-- 按钮组件 -->
      <a-card title="按钮组件" class="demo-card">
        <div class="button-group">
          <a-button type="primary">主要按钮</a-button>
          <a-button>默认按钮</a-button>
          <a-button type="dashed">虚线按钮</a-button>
          <a-button type="text">文本按钮</a-button>
          <a-button type="link">链接按钮</a-button>
        </div>
        <div class="button-group">
          <a-button type="primary" shape="circle">
            <template #icon><PlusOutlined /></template>
          </a-button>
          <a-button shape="circle">
            <template #icon><SearchOutlined /></template>
          </a-button>
          <a-button type="primary" shape="round">圆角按钮</a-button>
        </div>
      </a-card>

      <!-- 表单组件 -->
      <a-card title="表单组件" class="demo-card">
        <a-form layout="vertical">
          <a-form-item label="用户名">
            <a-input placeholder="请输入用户名" />
          </a-form-item>
          <a-form-item label="密码">
            <a-input-password placeholder="请输入密码" />
          </a-form-item>
          <a-form-item label="选择器">
            <a-select placeholder="请选择">
              <a-select-option value="option1">选项1</a-select-option>
              <a-select-option value="option2">选项2</a-select-option>
              <a-select-option value="option3">选项3</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="滑块">
            <a-slider :min="0" :max="100" :default-value="50" />
          </a-form-item>
          <a-form-item label="开关">
            <a-switch />
          </a-form-item>
        </a-form>
      </a-card>

      <!-- 数据展示组件 -->
      <a-card title="数据展示组件" class="demo-card">
        <a-list :data-source="listData" :bordered="false">
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta
                :avatar="item.avatar"
                :title="item.title"
                :description="item.description"
              />
            </a-list-item>
          </template>
        </a-list>
      </a-card>

      <!-- 反馈组件 -->
      <a-card title="反馈组件" class="demo-card">
        <div class="feedback-group">
          <a-button @click="showMessage">显示消息</a-button>
          <a-button @click="showNotification">显示通知</a-button>
          <a-button @click="showModal">显示弹窗</a-button>
        </div>
      </a-card>

      <!-- 导航组件 -->
      <a-card title="导航组件" class="demo-card">
        <a-menu mode="horizontal" :default-selected-keys="['1']">
          <a-menu-item key="1">
            <template #icon><HomeOutlined /></template>
            首页
          </a-menu-item>
          <a-menu-item key="2">
            <template #icon><UserOutlined /></template>
            用户
          </a-menu-item>
          <a-menu-item key="3">
            <template #icon><SettingOutlined /></template>
            设置
          </a-menu-item>
        </a-menu>
      </a-card>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { 
  EllipsisOutlined,
  LeftOutlined,
  PlusOutlined,
  SearchOutlined,
  HomeOutlined,
  UserOutlined,
  SettingOutlined
} from '@ant-design/icons-vue'
import { message, notification, Modal } from 'ant-design-vue'

export default {
  name: 'Demo',
  components: {
    EllipsisOutlined,
    LeftOutlined,
    PlusOutlined,
    SearchOutlined,
    HomeOutlined,
    UserOutlined,
    SettingOutlined
  },
  setup() {
    const listData = ref([
      {
        title: 'Ant Design Vue',
        description: '企业级 UI 设计语言和 React 组件库',
        avatar: 'https://gw.alipayobjects.com/zos/rmsportal/BiazfanxmamNRoxxVxka.png'
      },
      {
        title: 'Vue 3',
        description: '渐进式 JavaScript 框架',
        avatar: 'https://gw.alipayobjects.com/zos/rmsportal/BiazfanxmamNRoxxVxka.png'
      },
      {
        title: 'Vite',
        description: '下一代前端构建工具',
        avatar: 'https://gw.alipayobjects.com/zos/rmsportal/BiazfanxmamNRoxxVxka.png'
      }
    ])

    const goBack = () => {
      window.history.back()
    }

    const showMessage = () => {
      message.success('这是一条成功消息！')
    }

    const showNotification = () => {
      notification.info({
        message: '通知标题',
        description: '这是一条通知的描述信息',
        placement: 'topRight'
      })
    }

    const showModal = () => {
      Modal.info({
        title: '弹窗标题',
        content: '这是一个信息弹窗的内容',
        onOk() {
          console.log('OK')
        }
      })
    }

    return {
      listData,
      goBack,
      showMessage,
      showNotification,
      showModal
    }
  }
}
</script>

<style scoped>
.demo-page {
  min-height: 100vh;
  background-color: #f5f5f5;
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

.status-icon-btn {
  padding: 0;
  height: auto;
  color: #000000;
}

/* 页面头部 */
.page-header {
  margin: 0;
  border-radius: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-content {
  display: flex;
  align-items: center;
}

.back-btn {
  width: 36px;
  height: 36px;
  color: #666;
  margin-right: 12px;
}

.back-btn:hover {
  color: #007AFF;
  background-color: #f0f8ff;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #000000;
}

/* 演示内容 */
.demo-content {
  padding: 20px;
}

.demo-card {
  margin-bottom: 20px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.button-group {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.feedback-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .demo-content {
    padding: 16px;
  }
  
  .button-group,
  .feedback-group {
    gap: 8px;
  }
  
  .button-group .ant-btn,
  .feedback-group .ant-btn {
    font-size: 14px;
    padding: 4px 12px;
  }
}

/* Ant Design Vue 样式覆盖 */
:deep(.ant-card-head) {
  border-bottom: 1px solid #f0f0f0;
  padding: 0 20px;
}

:deep(.ant-card-head-title) {
  padding: 16px 0;
  font-weight: 600;
}

:deep(.ant-card-body) {
  padding: 20px;
}

:deep(.ant-form-item) {
  margin-bottom: 16px;
}

:deep(.ant-list-item) {
  padding: 12px 0 !important;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.ant-list-item:last-child) {
  border-bottom: none !important;
}

:deep(.ant-menu-horizontal) {
  border-bottom: none;
}
</style>
