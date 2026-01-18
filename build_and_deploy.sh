#!/bin/bash

echo "========================================"
echo "构建并部署到 Hugging Face Spaces"
echo "========================================"
echo ""

echo "[1/4] 构建前端..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "错误: npm install 失败"
    exit 1
fi

npm run build
if [ $? -ne 0 ]; then
    echo "错误: npm run build 失败"
    exit 1
fi
cd ..

echo ""
echo "[2/4] 检查构建产物..."
if [ ! -f "frontend/dist/index.html" ]; then
    echo "错误: 构建产物不存在"
    exit 1
fi
echo "✓ 构建产物检查通过"

echo ""
echo "[3/4] 提交到 Git..."
git add .
git commit -m "Build: Update frontend dist for deployment"
if [ $? -ne 0 ]; then
    echo "提示: 没有新的更改需要提交"
fi

echo ""
echo "[4/4] 推送到 Hugging Face..."
git push hf main
if [ $? -ne 0 ]; then
    echo "错误: 推送失败"
    echo "请检查 Hugging Face 远程仓库配置"
    exit 1
fi

echo ""
echo "========================================"
echo "✓ 部署完成！"
echo "========================================"
echo ""
echo "访问你的 Hugging Face Space 查看应用"
