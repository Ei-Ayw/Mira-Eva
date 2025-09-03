# Mira-Eva 快速启动指南

## 🚀 一键启动

### 方法一：使用启动脚本（推荐）

#### 启动后端
```bash
./start_backend.sh
```

#### 启动前端（新开一个终端）
```bash
./start_frontend.sh
```

### 方法二：手动启动

#### 1. 启动后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

#### 2. 启动前端（新开一个终端）
```bash
cd frontend
npm install
npm run dev
```

## 🌐 访问地址

- **前端页面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **管理后台**: http://localhost:8000/admin

## 📱 功能特性

### 已实现功能
- ✅ 基础聊天界面（H5移动端优化）
- ✅ AI回复生成（虚拟实现）
- ✅ 多模态消息支持（文字、语音、图片）
- ✅ WebSocket实时通信
- ✅ 响应式移动端设计

### 待完善功能
- 🔄 用户认证系统
- 🔄 腾讯云API集成
- 🔄 主动触发引擎
- 🔄 记忆系统
- 🔄 语音录制功能

## 🛠️ 开发说明

### 后端架构
- **Django**: 主框架
- **Django REST Framework**: API接口
- **Channels**: WebSocket支持
- **SQLite**: 开发数据库

### 前端架构
- **Vue 3**: 主框架
- **Vite**: 构建工具
- **Pinia**: 状态管理
- **移动端优先**: H5页面设计

### AI引擎
- **当前状态**: 虚拟实现，模拟AI回复
- **后续计划**: 集成腾讯云智能体平台

## 🔧 常见问题

### Q: 启动失败怎么办？
A: 检查Python版本（需要3.11+）和Node.js版本（需要18+）

### Q: 数据库迁移失败？
A: 删除`backend/db.sqlite3`文件，重新运行迁移命令

### Q: 前端无法连接后端？
A: 确保后端服务已启动，检查端口8000是否被占用

### Q: 如何修改AI回复？
A: 编辑`backend/ai_engine/core.py`中的回复模板

## 📝 开发计划

### 第一阶段（当前）
- [x] 基础项目架构
- [x] 聊天界面
- [x] 虚拟AI回复

### 第二阶段
- [ ] 用户认证
- [ ] 腾讯云API集成
- [ ] 语音功能

### 第三阶段
- [ ] 主动触发
- [ ] 记忆系统
- [ ] 高级功能

## 🎯 下一步

1. 完善用户认证系统
2. 集成腾讯云智能体平台
3. 实现语音录制和播放
4. 添加主动触发功能
5. 构建记忆系统

---

**开始你的数字朋友之旅吧！** 🌟
