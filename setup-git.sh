#!/bin/bash

# 设置Git仓库并推送到GitHub
echo "🚀 开始设置Git仓库..."

# 检查是否已经初始化
if [ -d ".git" ]; then
    echo "⚠️  Git仓库已经存在"
else
    echo "📁 初始化Git仓库..."
    git init
fi

# 添加所有文件
echo "📝 添加文件到暂存区..."
git add .

# 提交更改
echo "💾 提交更改..."
git commit -m "Initial commit: Crypto GEX Dashboard with deployment config"

# 设置主分支名称
git branch -M main

echo "🔗 请手动添加GitHub远程仓库:"
echo "git remote add origin https://github.com/YOUR_USERNAME/crypto-gex-dashboard-v2.git"
echo "git push -u origin main"

echo "✅ Git设置完成！"
echo ""
echo "📋 接下来的步骤："
echo "1. 在GitHub上创建新仓库"
echo "2. 运行上面的git remote命令（替换YOUR_USERNAME）"
echo "3. 按照 deploy.md 中的指南部署到Railway和Vercel" 