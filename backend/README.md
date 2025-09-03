# Mira-Eva 后端API文档

## 项目概述

Mira-Eva是一个数字孪生朋友AI系统，提供智能聊天、个人资料管理、记忆系统和个性化设置等功能。

## 技术栈

- **Django 5.0.2** - Web框架
- **Django REST Framework** - API框架
- **Channels** - WebSocket支持
- **SQLite** - 数据库（开发环境）
- **Pillow** - 图像处理

## 应用结构

### 1. 聊天系统 (chat_system)

#### 模型
- `ChatSession` - 聊天会话
- `Message` - 消息记录
- `AudioFile` - 音频文件
- `ImageFile` - 图片文件

#### API端点
```
GET    /api/chat/sessions/           # 获取聊天会话列表
POST   /api/chat/sessions/           # 创建新会话
POST   /api/chat/sessions/{id}/close_session/  # 关闭会话
GET    /api/chat/messages/           # 获取消息列表
POST   /api/chat/messages/           # 发送新消息
GET    /api/chat/messages/chat_history/  # 获取聊天历史
POST   /api/chat/upload/             # 文件上传
GET    /api/chat/stats/              # 聊天统计
```

#### WebSocket
```
ws://localhost:8000/ws/chat/{session_id}/
```

### 2. 用户资料 (user_profile)

#### 模型
- `UserProfile` - 用户资料
- `Memory` - 记忆系统
- `UserStats` - 用户统计

#### API端点
```
GET    /api/profile/profile/         # 获取用户资料
PUT    /api/profile/profile/         # 更新用户资料
POST   /api/profile/profile/update_avatar/  # 更新头像
GET    /api/profile/profile/summary/ # 获取资料摘要
GET    /api/profile/memories/        # 获取记忆列表
POST   /api/profile/memories/        # 创建新记忆
GET    /api/profile/memories/by_type/  # 按类型获取记忆
POST   /api/profile/memories/{id}/access/  # 记录记忆访问
GET    /api/profile/stats/           # 获取用户统计
POST   /api/profile/stats/           # 更新统计信息
GET    /api/profile/analytics/       # 记忆分析
```

### 3. 用户设置 (user_settings)

#### 模型
- `UserSettings` - 用户设置
- `NotificationPreference` - 通知偏好
- `UserActivity` - 用户活动

#### API端点
```
GET    /api/settings/settings/       # 获取用户设置
PUT    /api/settings/settings/       # 更新用户设置
GET    /api/settings/settings/ai_personality/  # 获取AI个性设置
PUT    /api/settings/settings/ai_personality/  # 更新AI个性设置
GET    /api/settings/settings/notifications/   # 获取通知设置
PUT    /api/settings/settings/notifications/   # 更新通知设置
GET    /api/settings/settings/features/        # 获取功能设置
PUT    /api/settings/settings/features/        # 更新功能设置
GET    /api/settings/settings/interface/       # 获取界面设置
PUT    /api/settings/settings/interface/       # 更新界面设置
POST   /api/settings/settings/reset_to_default/  # 重置为默认值
GET    /api/settings/settings/export/          # 导出设置
POST   /api/settings/settings/import_settings/  # 导入设置
GET    /api/settings/notifications/            # 获取通知偏好
POST   /api/settings/notifications/            # 创建通知偏好
GET    /api/settings/activities/               # 获取活动记录
GET    /api/settings/activities/recent/        # 获取最近活动
GET    /api/settings/activities/by_type/       # 按类型获取活动
```

## 数据模型关系

```
User (Django内置)
├── UserProfile (一对一)
├── UserSettings (一对一)
├── UserStats (一对一)
├── ChatSession (一对多)
│   └── Message (一对多)
│       ├── AudioFile (一对一)
│       └── ImageFile (一对一)
├── Memory (一对多)
│   └── MemoryAccess (一对多)
├── NotificationPreference (一对多)
└── UserActivity (一对多)
```

## 认证和权限

- 所有API端点都需要用户认证
- 使用Django内置的Session认证
- 支持Token认证（可选）
- 用户只能访问自己的数据

## 文件上传

支持的文件类型：
- **图片**: JPG, PNG, GIF等
- **音频**: MP3, WAV, M4A等

文件存储路径：
- 图片: `media/image_messages/`
- 音频: `media/audio_messages/`
- 头像: `media/avatars/`

## 开发环境设置

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行数据库迁移：
```bash
python manage.py makemigrations
python manage.py migrate
```

4. 创建超级用户：
```bash
python manage.py createsuperuser
```

5. 启动开发服务器：
```bash
python manage.py runserver
```

## 生产环境部署

- 使用PostgreSQL替代SQLite
- 配置Redis作为Channels后端
- 设置适当的CORS策略
- 配置静态文件和媒体文件服务
- 使用Gunicorn或uWSGI作为WSGI服务器

## API响应格式

### 成功响应
```json
{
    "id": 1,
    "message": "操作成功",
    "data": {...}
}
```

### 错误响应
```json
{
    "error": "错误描述",
    "detail": "详细错误信息"
}
```

## WebSocket消息格式

### 发送消息
```json
{
    "type": "chat_message",
    "content": "消息内容",
    "content_type": "text",
    "text": "图片说明",
    "alt": "图片alt属性",
    "duration": 15
}
```

### 接收消息
```json
{
    "type": "chat_message",
    "message": {
        "id": 123,
        "content_type": "text",
        "sender": "user",
        "content": "消息内容",
        "timestamp": "2024-01-01T12:00:00Z",
        "formatted_time": "12:00 PM"
    }
}
```

## 测试

运行测试：
```bash
python manage.py test
```

## 贡献

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License
