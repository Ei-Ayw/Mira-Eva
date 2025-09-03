#!/bin/bash

# Mira Eva 前端开发服务器启动脚本

echo "🚀 启动 Mira Eva 前端开发服务器..."

# 检查Node.js版本
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到Node.js，请先安装Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ 错误: Node.js版本过低，需要18+，当前版本: $(node -v)"
    exit 1
fi

echo "✅ Node.js版本: $(node -v)"

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: 未找到npm，请先安装npm"
    exit 1
fi

echo "✅ npm版本: $(npm -v)"

# 检查依赖是否已安装
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装"
fi

# 启动开发服务器
echo "🌐 启动开发服务器..."
echo "📍 本地访问地址: http://localhost:5173"
echo "📱 移动端测试: 使用手机访问 http://[你的IP]:5173"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

npm run dev
