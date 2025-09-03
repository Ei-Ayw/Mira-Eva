# Mira-Eva 数字孪生朋友AI系统

## 🎯 项目概述

Mira-Eva是一个智能聊天系统，提供AI朋友交互、个人资料管理、记忆系统和个性化设置等功能。系统采用前后端分离架构，支持实时聊天、多媒体消息和智能记忆管理。

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (Vue 3)  │    │   后端 (Django) │    │   数据库        │
│                 │    │                 │    │                 │
│ • 聊天界面      │◄──►│ • REST API      │◄──►│ • SQLite       │
│ • 个人资料      │    │ • WebSocket     │    │ • 用户数据      │
│ • 设置页面      │    │ • 认证系统      │    │ • 聊天记录      │
│ • 响应式设计    │    │ • 文件上传      │    │ • 记忆系统      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ✨ 主要功能

### 💬 智能聊天
- 实时WebSocket通信
- 支持文字、语音、图片消息
- AI智能回复（模拟）
- 聊天历史记录
- 会话管理

### 👤 个人资料
- 用户信息管理
- 智能记忆系统
- 记忆分类（事实、事件、偏好等）
- 统计分析
- 头像上传

### ⚙️ 个性化设置
- AI个性配置（热情度、健谈度等）
- 通知偏好设置
- 功能开关控制
- 界面主题选择
- 设置导入导出

## 🚀 快速开始

### 环境要求
- Node.js 18+
- Python 3.8+
- SQLite 3

### 后端启动
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 访问系统
- 前端: http://localhost:5173
- 后端API: http://localhost:8000/api
- 管理后台: http://localhost:8000/admin
- 演示账号: admin / admin123

## 🔧 技术栈

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Composition API** - 组合式API
- **Vue Router 4** - 路由管理
- **Ant Design Vue** - UI组件库
- **WebSocket** - 实时通信

### 后端
- **Django 5.0** - Web框架
- **Django REST Framework** - API框架
- **Channels** - WebSocket支持
- **SQLite** - 数据库
- **Pillow** - 图像处理

## 📡 API接口

### 认证
- 所有API都需要用户认证
- 支持Token认证
- 自动认证状态检查

### 聊天系统
```
POST   /api/chat/sessions/create_session/    # 创建会话
GET    /api/chat/messages/chat_history/      # 聊天历史
POST   /api/chat/messages/                   # 发送消息
POST   /api/chat/upload/                     # 文件上传
GET    /api/chat/stats/                      # 聊天统计
```

### 用户资料
```
GET    /api/profile/profile/summary/         # 资料摘要
PUT    /api/profile/profile/                 # 更新资料
GET    /api/profile/memories/                # 记忆列表
GET    /api/profile/analytics/               # 记忆分析
```

### 用户设置
```
GET    /api/settings/settings/ai_personality/    # AI个性设置
PUT    /api/settings/settings/ai_personality/    # 更新AI个性
GET    /api/settings/settings/notifications/     # 通知设置
POST   /api/settings/settings/reset_to_default/  # 重置设置
```

### WebSocket
```
ws://localhost:8000/ws/chat/{session_id}/
```

## 🗄️ 数据模型

### 核心实体
- **User** - 用户基础信息
- **ChatSession** - 聊天会话
- **Message** - 消息记录
- **Memory** - 智能记忆
- **UserSettings** - 用户设置

### 关系图
```
User (1) ── (1) UserProfile
User (1) ── (1) UserSettings
User (1) ── (1) UserStats
User (1) ── (n) ChatSession
ChatSession (1) ── (n) Message
Message (1) ── (1) AudioFile/ImageFile
User (1) ── (n) Memory
```

## 🔒 安全特性

- 用户认证和授权
- API访问控制
- 文件上传安全
- CORS配置
- 数据验证

## 📱 移动端适配

- 响应式设计
- 触摸优化
- 移动端手势
- 自适应布局

## 🧪 测试

### 后端API测试
```bash
cd backend
python test_api.py
```

### 前端功能测试
- 登录认证
- 聊天功能
- 个人资料
- 设置管理

## 🚧 开发状态

### ✅ 已完成
- [x] 后端API架构
- [x] 数据模型设计
- [x] 认证系统
- [x] 聊天基础功能
- [x] 用户资料管理
- [x] 设置系统
- [x] 前端界面
- [x] WebSocket集成
- [x] 文件上传

### 🔄 进行中
- [ ] AI引擎集成
- [ ] 语音识别
- [ ] 图像生成
- [ ] 智能记忆算法

### 📋 计划中
- [ ] 多语言支持
- [ ] 移动端应用
- [ ] 云端部署
- [ ] 性能优化

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## 📞 联系方式

- 项目地址: [GitHub Repository]
- 问题反馈: [Issues]
- 功能建议: [Discussions]

---

**Mira-Eva** - 让AI成为你的数字朋友 🤖✨
# Mira-Eva
