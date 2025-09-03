#!/bin/bash

echo "🚀 启动 Mira-Eva 后端服务..."

# 检查Python版本
python_version=$(python3 --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.11+"
    exit 1
fi

echo "✅ Python版本: $python_version"

# 进入后端目录
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装Python依赖..."
pip install -r requirements.txt

# 检查数据库
if [ ! -f "db.sqlite3" ]; then
    echo "🗄️ 初始化数据库..."
    python manage.py makemigrations
    python manage.py migrate
    
    echo "👤 创建超级用户..."
    echo "请按提示输入用户名、邮箱和密码"
    python manage.py createsuperuser
fi

# 启动服务器
echo "🌐 启动Django服务器..."
echo "📍 后端地址: http://localhost:8000"
echo "📍 管理后台: http://localhost:8000/admin"
echo "📍 API文档: http://localhost:8000/api/"
echo ""
echo "按 Ctrl+C 停止服务器"

python manage.py runserver 0.0.0.0:8000
