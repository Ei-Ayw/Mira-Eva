# Mira Eva 前端应用

这是一个基于Vue 3的移动端AI助手应用，提供与Mira的智能对话体验。使用Ant Design Vue组件库构建，界面美观、交互友好。

## 🎨 设计特色

### **Ant Design Vue 组件库**
- **专业UI组件**: 使用[Ant Design Vue](https://antdv.com/components/overview)提供的高质量组件
- **一致的设计语言**: 遵循Ant Design设计规范，界面统一美观
- **丰富的交互组件**: 包含Button、Card、Avatar、Slider、Switch、List等组件
- **响应式设计**: 完美适配移动端和桌面端设备

### **视觉设计**
- **现代化界面**: 采用卡片式布局，层次分明
- **渐变色彩**: 使用渐变色增强视觉层次感
- **阴影效果**: 适当的阴影营造立体感
- **图标系统**: 使用Ant Design图标库，图标统一美观

## 功能特性

### 🗨️ 聊天页面 (Chat.vue)
- **智能对话**: 与Mira进行文字、语音和图片交流
- **多模态消息**: 支持文字、语音和图片消息类型
- **实时通信**: 基于WebSocket的实时消息传输
- **语音输入**: 支持语音录制和发送
- **响应式设计**: 完全适配移动端设备
- **Ant Design组件**: 使用Card、Avatar、Button、Textarea等组件

### 👤 个人资料页面 (Profile.vue)
- **用户信息**: 显示用户基本信息和头像
- **记忆统计**: 展示Mira了解的用户信息数量
- **分类管理**: 按事实、事件、偏好分类显示记忆
- **交互式界面**: 点击可查看各类别的详细信息
- **Ant Design组件**: 使用Card、Avatar、Tag、List等组件

### ⚙️ 设置页面 (Settings.vue)
- **个性化设置**: 调整Mira的热情度和话痨程度
- **通知管理**: 控制主动消息的接收
- **技能开关**: 启用/禁用图片生成和语音消息功能
- **版本信息**: 查看应用版本和关于信息
- **Ant Design组件**: 使用Card、Slider、Switch、List等组件

## 技术架构

- **框架**: Vue 3 + Composition API
- **路由**: Vue Router 4
- **状态管理**: Pinia (stores)
- **UI组件库**: [Ant Design Vue 4.x](https://antdv.com/components/overview)
- **样式**: CSS3 + 移动端优化
- **通信**: WebSocket实时通信
- **音频**: 原生Web Audio API

## 页面导航

```
Chat (/) ←→ Profile (/profile)
   ↕
Settings (/settings)
```

## 移动端优化

- **触摸友好**: 优化的触摸交互体验
- **安全区域**: 支持iPhone刘海屏等特殊设备
- **性能优化**: 流畅的动画和过渡效果
- **响应式设计**: 适配各种屏幕尺寸

## 开发说明

### 启动开发服务器
```bash
cd frontend
./start_dev.sh
```

或者手动运行：
```bash
npm install
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 代码规范
- 使用Vue 3 Composition API
- 组件命名采用PascalCase
- 样式使用scoped CSS
- 中文注释说明功能
- 优先使用Ant Design Vue组件

## 设计规范

### 颜色系统
- **主色调**: #007AFF (iOS蓝)
- **辅助色**: #34C759 (绿色), #FF9500 (橙色)
- **背景色**: #FFFFFF (白色), #F8F9FA (浅灰)
- **文字色**: #000000 (黑色), #8E8E93 (灰色)

### 字体系统
- **主字体**: -apple-system, BlinkMacSystemFont
- **中文字体**: PingFang SC, Hiragino Sans GB
- **字号**: 14px (小), 16px (标准), 18px (大), 20px (标题)

### 间距系统
- **基础间距**: 8px, 12px, 16px, 20px
- **圆角**: 8px (小), 16px (中), 18px (大), 50% (圆形)

### 组件使用规范
- **Card组件**: 用于内容分组和布局
- **Avatar组件**: 用于用户头像显示
- **Button组件**: 统一按钮样式和交互
- **Slider组件**: 用于数值范围选择
- **Switch组件**: 用于开关状态切换
- **List组件**: 用于列表数据展示

## 浏览器支持

- iOS Safari 12+
- Chrome Mobile 70+
- Firefox Mobile 68+
- Samsung Internet 10+

## 注意事项

1. 语音功能需要HTTPS环境
2. 图片上传功能需要后端支持
3. WebSocket连接需要后端服务运行
4. 移动端建议使用最新版本浏览器
5. Ant Design Vue组件需要Vue 3.3+版本支持

## 组件库优势

使用Ant Design Vue组件库带来的好处：

- **开发效率**: 丰富的预制组件，减少重复开发
- **设计一致性**: 统一的设计语言和交互模式
- **可访问性**: 符合WCAG标准的无障碍设计
- **主题定制**: 支持主题色和样式自定义
- **国际化**: 内置多语言支持
- **TypeScript**: 完整的类型定义支持
