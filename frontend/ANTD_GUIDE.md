# Ant Design Vue 组件使用指南

本指南介绍如何在Mira Eva项目中使用Ant Design Vue组件库，让界面更加美观和专业。

## 🚀 快速开始

### 安装依赖
```bash
npm install ant-design-vue@4.x
```

### 引入组件库
```javascript
// main.js
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'

app.use(Antd)
```

### 引入图标
```javascript
import { 
  UserOutlined, 
  SettingOutlined, 
  RobotOutlined 
} from '@ant-design/icons-vue'

export default {
  components: {
    UserOutlined,
    SettingOutlined,
    RobotOutlined
  }
}
```

## 🎨 核心组件使用

### 1. 布局组件

#### Card 卡片
```vue
<template>
  <a-card title="卡片标题" :bordered="false">
    <p>卡片内容</p>
  </a-card>
</template>
```

**常用属性:**
- `title`: 卡片标题
- `bordered`: 是否显示边框
- `size`: 卡片大小 (small/default)
- `hoverable`: 是否可悬停

#### Avatar 头像
```vue
<template>
  <a-avatar 
    :size="64" 
    :style="{ background: 'linear-gradient(135deg, #007AFF, #5AC8FA)' }"
  >
    <template #icon><RobotOutlined /></template>
  </a-avatar>
</template>
```

**常用属性:**
- `size`: 头像大小
- `src`: 图片地址
- `icon`: 图标

### 2. 表单组件

#### Input 输入框
```vue
<template>
  <a-input 
    v-model:value="inputValue"
    placeholder="请输入内容"
    :maxlength="100"
  />
</template>
```

#### Textarea 文本域
```vue
<template>
  <a-textarea 
    v-model:value="textValue"
    placeholder="请输入多行文本"
    :rows="4"
    :auto-size="{ minRows: 2, maxRows: 6 }"
  />
</template>
```

#### Select 选择器
```vue
<template>
  <a-select 
    v-model:value="selectedValue"
    placeholder="请选择"
    style="width: 100%"
  >
    <a-select-option value="option1">选项1</a-select-option>
    <a-select-option value="option2">选项2</a-select-option>
  </a-select>
</template>
```

#### Slider 滑块
```vue
<template>
  <a-slider
    v-model:value="sliderValue"
    :min="0"
    :max="100"
    :step="5"
    @change="handleChange"
  />
</template>
```

#### Switch 开关
```vue
<template>
  <a-switch
    v-model:checked="switchValue"
    @change="handleChange"
  />
</template>
```

### 3. 按钮组件

#### Button 按钮
```vue
<template>
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
    <a-button shape="round">圆角按钮</a-button>
  </div>
</template>
```

**常用属性:**
- `type`: 按钮类型 (primary/ghost/dashed/link/text)
- `shape`: 按钮形状 (circle/round)
- `size`: 按钮大小 (large/default/small)
- `icon`: 图标

### 4. 数据展示组件

#### List 列表
```vue
<template>
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
</template>

<script>
const listData = [
  {
    title: '标题',
    description: '描述信息',
    avatar: 'https://example.com/avatar.png'
  }
]
</script>
```

#### Tag 标签
```vue
<template>
  <div class="tag-group">
    <a-tag color="blue">蓝色标签</a-tag>
    <a-tag color="green">绿色标签</a-tag>
    <a-tag color="orange">橙色标签</a-tag>
    <a-tag color="red">红色标签</a-tag>
  </div>
</template>
```

### 5. 反馈组件

#### Message 消息提示
```vue
<template>
  <a-button @click="showMessage">显示消息</a-button>
</template>

<script>
import { message } from 'ant-design-vue'

const showMessage = () => {
  message.success('操作成功！')
  message.error('操作失败！')
  message.warning('警告信息！')
  message.info('提示信息！')
}
</script>
```

#### Notification 通知提醒
```vue
<template>
  <a-button @click="showNotification">显示通知</a-button>
</template>

<script>
import { notification } from 'ant-design-vue'

const showNotification = () => {
  notification.success({
    message: '成功',
    description: '操作已完成',
    placement: 'topRight'
  })
}
</script>
```

#### Modal 对话框
```vue
<template>
  <a-button @click="showModal">显示弹窗</a-button>
</template>

<script>
import { Modal } from 'ant-design-vue'

const showModal = () => {
  Modal.confirm({
    title: '确认',
    content: '确定要执行此操作吗？',
    onOk() {
      console.log('确认')
    },
    onCancel() {
      console.log('取消')
    }
  })
}
</script>
```

## 🎯 样式定制

### 使用CSS变量
```css
:root {
  --ant-primary-color: #007AFF;
  --ant-border-radius-base: 8px;
  --ant-box-shadow-base: 0 2px 8px rgba(0, 0, 0, 0.1);
}
```

### 深度选择器
```vue
<style scoped>
/* 覆盖Ant Design Vue组件样式 */
:deep(.ant-card-head) {
  border-bottom: 1px solid #f0f0f0;
  padding: 0 20px;
}

:deep(.ant-btn-primary) {
  background: linear-gradient(135deg, #007AFF, #0056b3);
  border: none;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.3);
}
</style>
```

### 主题定制
```javascript
// 在main.js中配置主题
import { ConfigProvider } from 'ant-design-vue'

app.use(ConfigProvider, {
  theme: {
    token: {
      colorPrimary: '#007AFF',
      borderRadius: 8,
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
    }
  }
})
```

## 📱 移动端适配

### 响应式设计
```vue
<template>
  <a-card class="responsive-card">
    <div class="content">
      <!-- 内容 -->
    </div>
  </a-card>
</template>

<style scoped>
.responsive-card {
  margin: 20px;
}

@media (max-width: 480px) {
  .responsive-card {
    margin: 16px;
  }
  
  .content {
    font-size: 14px;
  }
}
</style>
```

### 触摸优化
```css
/* 触摸友好的按钮大小 */
.ant-btn {
  min-height: 44px;
  min-width: 44px;
}

/* 禁用触摸高亮 */
* {
  -webkit-tap-highlight-color: transparent;
}
```

## 🔧 最佳实践

### 1. 组件导入
```javascript
// 推荐：按需导入
import { Button, Card, Avatar } from 'ant-design-vue'

// 不推荐：全量导入
import Antd from 'ant-design-vue'
```

### 2. 图标使用
```javascript
// 推荐：使用图标组件
import { UserOutlined } from '@ant-design/icons-vue'

// 不推荐：使用Unicode字符
<span>👤</span>
```

### 3. 样式组织
```vue
<style scoped>
/* 1. 基础样式 */
.component {
  /* 基础样式 */
}

/* 2. 状态样式 */
.component:hover {
  /* 悬停状态 */
}

/* 3. 响应式样式 */
@media (max-width: 768px) {
  .component {
    /* 移动端样式 */
  }
}

/* 4. 深度选择器 */
:deep(.ant-component) {
  /* 覆盖组件样式 */
}
</style>
```

### 4. 性能优化
```vue
<template>
  <!-- 使用v-show而不是v-if进行频繁切换 -->
  <div v-show="isVisible" class="content">
    内容
  </div>
  
  <!-- 使用key优化列表渲染 -->
  <a-list-item 
    v-for="item in items" 
    :key="item.id"
  >
    {{ item.name }}
  </a-list-item>
</template>
```

## 📚 资源链接

- [Ant Design Vue 官方文档](https://antdv.com/components/overview)
- [Ant Design Vue GitHub](https://github.com/vueComponent/ant-design-vue)
- [Ant Design 设计语言](https://ant.design/docs/spec/introduce-cn)
- [Vue 3 官方文档](https://cn.vuejs.org/)

## 🎉 总结

使用Ant Design Vue组件库可以：

1. **提高开发效率** - 丰富的预制组件
2. **保证设计一致性** - 统一的设计语言
3. **增强用户体验** - 专业的交互设计
4. **支持主题定制** - 灵活的品牌适配
5. **提供完整文档** - 详细的使用说明

通过合理使用这些组件，可以让Mira Eva应用拥有更加专业和美观的用户界面！
