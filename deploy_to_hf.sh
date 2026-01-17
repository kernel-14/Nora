#!/bin/bash

# Hugging Face Spaces 快速部署脚本

echo "🚀 开始部署到 Hugging Face Spaces..."

# 检查是否已登录
if ! huggingface-cli whoami &> /dev/null; then
    echo "❌ 请先登录 Hugging Face CLI"
    echo "运行: huggingface-cli login"
    exit 1
fi

# 获取用户名
USERNAME=$(huggingface-cli whoami | grep "username:" | awk '{print $2}')
echo "✅ 已登录为: $USERNAME"

# 询问 Space 名称
read -p "请输入 Space 名称 (默认: soulmate-ai-companion): " SPACE_NAME
SPACE_NAME=${SPACE_NAME:-soulmate-ai-companion}

echo "📦 准备文件..."

# 构建前端
echo "🔨 构建前端..."
cd frontend
npm install
npm run build
cd ..

if [ ! -d "frontend/dist" ]; then
    echo "❌ 前端构建失败"
    exit 1
fi

echo "✅ 前端构建完成"

# 创建临时目录
TEMP_DIR="temp_hf_deploy"
rm -rf $TEMP_DIR
mkdir -p $TEMP_DIR

# 复制文件
echo "📋 复制文件..."
cp app.py $TEMP_DIR/
cp requirements_hf.txt $TEMP_DIR/requirements.txt
cp README_HF.md $TEMP_DIR/README.md
cp .gitattributes $TEMP_DIR/
cp -r app $TEMP_DIR/
cp -r frontend/dist $TEMP_DIR/frontend/
mkdir -p $TEMP_DIR/data
mkdir -p $TEMP_DIR/generated_images

# 创建或克隆 Space
echo "🌐 准备 Space..."
SPACE_URL="https://huggingface.co/spaces/$USERNAME/$SPACE_NAME"

if huggingface-cli repo info "spaces/$USERNAME/$SPACE_NAME" &> /dev/null; then
    echo "✅ Space 已存在，克隆中..."
    cd $TEMP_DIR
    git clone $SPACE_URL .
else
    echo "🆕 创建新 Space..."
    huggingface-cli repo create $SPACE_NAME --type space --space_sdk gradio
    cd $TEMP_DIR
    git clone $SPACE_URL .
fi

# 复制文件到仓库
echo "📤 准备上传..."
cp ../app.py .
cp ../requirements_hf.txt ./requirements.txt
cp ../README_HF.md ./README.md
cp ../.gitattributes .
cp -r ../app .
cp -r ../frontend/dist ./frontend/
mkdir -p data generated_images

# 提交并推送
echo "🚀 上传到 Hugging Face..."
git add .
git commit -m "Deploy to Hugging Face Spaces"
git push

cd ..
rm -rf $TEMP_DIR

echo ""
echo "✅ 部署完成！"
echo ""
echo "📍 Space URL: $SPACE_URL"
echo ""
echo "⚙️  下一步："
echo "1. 访问 $SPACE_URL"
echo "2. 点击 Settings → Repository secrets"
echo "3. 添加环境变量："
echo "   - ZHIPU_API_KEY (必需)"
echo "   - MINIMAX_API_KEY (可选)"
echo "   - MINIMAX_GROUP_ID (可选)"
echo ""
echo "🎉 完成后即可使用！"
