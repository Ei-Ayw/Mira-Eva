#!/bin/bash

echo "🎨 启动 Mira-Eva 前端服务..."

# 检查Node.js版本
node_version=$(node --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo "❌ 错误: 未找到Node.js，请先安装Node.js 18+"
    exit 1
fi

echo "✅ Node.js版本: $node_version"

# 检查npm版本
npm_version=$(npm --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo "❌ 错误: 未找到npm，请先安装npm"
    exit 1
fi

echo "✅ npm版本: $npm_version"

# 进入前端目录
cd frontend

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 启动开发服务器
echo "🌐 启动Vue开发服务器..."
echo "📍 前端地址: http://localhost:3000"
echo "📍 后端代理: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服务器"

npm run dev
