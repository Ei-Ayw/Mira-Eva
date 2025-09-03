#!/bin/bash

# Mira Eva 前端快速启动脚本 - Ant Design Vue 版本

echo "🎨 Mira Eva 前端应用 - Ant Design Vue 版本"
echo "=========================================="

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到Node.js，请先安装Node.js 18+"
    exit 1
fi

echo "✅ Node.js版本: $(node -v)"

# 检查依赖
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

# 检查Ant Design Vue
if npm list ant-design-vue &> /dev/null; then
    echo "✅ Ant Design Vue 已安装"
else
    echo "📦 安装 Ant Design Vue..."
    npm install ant-design-vue@4.x
    echo "✅ Ant Design Vue 安装完成"
fi

echo ""
echo "🚀 启动开发服务器..."
echo "📍 本地访问地址: http://localhost:5173"
echo "🎯 演示页面: http://localhost:5173/demo"
echo "💬 聊天页面: http://localhost:5173/chat"
echo "👤 个人资料: http://localhost:5173/profile"
echo "⚙️ 设置页面: http://localhost:5173/settings"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

npm run dev
