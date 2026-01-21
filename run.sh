#!/bin/bash

# Excel色阶处理Agent启动脚本

echo "🎨 Excel色阶处理Agent Demo"
echo "================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    echo "请先安装Python3: https://www.python.org/downloads/"
    exit 1
fi

# 检查依赖是否安装
echo "📦 检查依赖..."
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "⚠️  检测到未安装依赖，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装"
fi

# 检查AWS凭证
echo ""
echo "🔐 检查AWS凭证..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "⚠️  警告: AWS凭证未配置或无效"
    echo "请运行: aws configure"
    echo "或设置环境变量: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
    echo ""
    read -p "是否继续启动? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ AWS凭证已配置"
fi

# 创建temp目录
echo ""
echo "📁 准备临时目录..."
mkdir -p temp
echo "✅ 临时目录已创建"

# 启动Streamlit
echo ""
echo "🚀 启动应用..."
echo "================================"
echo ""
streamlit run app.py
