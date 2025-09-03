# 文档处理系统

## 功能概述

文档处理系统允许用户上传 PDF、Word、Markdown 等格式的文档，系统会自动解析文档内容，提取文本，并进行智能分块，最终形成可用的学习材料。

## 支持的文件格式

- **PDF** (.pdf) - 使用 PyPDF2 库提取文本
- **Word** (.docx, .doc) - 使用 python-docx 库提取文本
- **Markdown** (.md, .markdown) - 直接读取并解析结构
- **纯文本** (.txt) - 直接读取

## 系统架构

### 数据模型

1. **Document** - 文档主表
   - 基本信息：标题、文件类型、大小、状态
   - 处理结果：提取的文本、摘要、关键词
   - 时间戳：上传时间、处理完成时间

2. **DocumentChunk** - 文档分块表
   - 分块类型：段落、对话、示例、说明、其他
   - 内容：分块后的文本内容
   - 元数据：长度、是否包含问题/感叹号等

3. **LearningPackage** - 学习包表
   - 包类型：对话示例、知识库、训练材料、参考资料
   - 关联文档：可以包含多个文档
   - 统计信息：总分块数、总示例数

### 处理流程

1. **文件上传** - 用户选择文件并上传
2. **格式检测** - 系统自动识别文件类型
3. **文本提取** - 根据文件类型调用相应的处理器
4. **内容分块** - 智能分割文本为有意义的片段
5. **类型分类** - 自动识别分块类型（对话、示例等）
6. **存储入库** - 保存到数据库，供后续使用

## API 接口

### 文档管理

- `POST /api/documents/` - 上传文档
- `GET /api/documents/` - 获取文档列表
- `GET /api/documents/{id}/` - 获取文档详情
- `POST /api/documents/{id}/reprocess/` - 重新处理文档
- `DELETE /api/documents/{id}/` - 删除文档
- `GET /api/documents/stats/` - 获取文档统计

### 学习包管理

- `POST /api/packages/` - 创建学习包
- `GET /api/packages/` - 获取学习包列表
- `GET /api/packages/{id}/` - 获取学习包详情
- `PUT /api/packages/{id}/` - 更新学习包
- `DELETE /api/packages/{id}/` - 删除学习包
- `POST /api/packages/{id}/add_documents/` - 添加文档到学习包
- `POST /api/packages/{id}/remove_documents/` - 从学习包移除文档

## 使用方法

### 1. 上传文档

```bash
curl -X POST http://localhost:8000/api/documents/ \
  -H "Authorization: Bearer <your_jwt_token>" \
  -F "file=@example_document.md" \
  -F "title=高情商对话示例"
```

### 2. 创建学习包

```bash
curl -X POST http://localhost:8000/api/packages/ \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "沟通技巧学习包",
    "description": "包含高情商对话示例和职场沟通技巧",
    "package_type": "conversation",
    "document_ids": [1, 2, 3]
  }'
```

### 3. 查看文档分块

```bash
curl -X GET http://localhost:8000/api/documents/1/ \
  -H "Authorization: Bearer <your_jwt_token>"
```

## 前端页面

访问 `/documents` 路径可以看到完整的文档管理界面，包括：

- 拖拽上传区域
- 文档列表和状态管理
- 学习包创建和管理
- 文档内容预览和分块查看

## 配置要求

### 依赖库

```bash
pip install PyPDF2 python-docx
```

### 环境变量

- `MEDIA_ROOT` - 文档存储目录
- `MEDIA_URL` - 文档访问URL

### 数据库

需要运行以下命令创建数据表：

```bash
python manage.py makemigrations document_processor
python manage.py migrate
```

## 扩展功能

### 1. 异步处理

当前版本使用同步处理，可以扩展为异步处理以提高性能：

```python
from celery import shared_task

@shared_task
def process_document_async(document_id):
    # 异步处理文档
    pass
```

### 2. 智能分块

可以集成更先进的 NLP 技术进行智能分块：

```python
from transformers import pipeline

def intelligent_chunking(text):
    # 使用预训练模型进行智能分块
    pass
```

### 3. 内容分析

可以添加更多内容分析功能：

- 情感分析
- 主题提取
- 关键信息识别
- 相似度计算

## 注意事项

1. **文件大小限制** - 建议限制单个文件不超过 10MB
2. **文件类型验证** - 严格验证文件类型，防止恶意文件上传
3. **存储空间** - 注意监控媒体文件存储空间使用情况
4. **处理性能** - 大文件处理可能需要较长时间，建议添加进度提示

## 故障排除

### 常见问题

1. **PDF 文本提取失败**
   - 检查 PyPDF2 是否正确安装
   - 确认 PDF 文件不是扫描版（图片版）

2. **Word 文档处理失败**
   - 检查 python-docx 是否正确安装
   - 确认文档格式是否损坏

3. **文件上传失败**
   - 检查文件大小是否超限
   - 确认文件类型是否支持
   - 验证用户权限和认证状态

### 日志查看

```bash
# 查看文档处理日志
tail -f logs/mira_eva.log | grep document_processor

# 查看错误日志
tail -f logs/error.log
```

## 更新日志

- **v1.0.0** - 初始版本，支持基础文档处理功能
- 支持 PDF、Word、Markdown、TXT 格式
- 智能分块和类型识别
- 学习包管理功能
- 完整的 API 接口
