---
title: Nora - 治愈系记录助手
emoji: 🌟
colorFrom: purple
colorTo: pink
sdk: docker
pinned: false
license: mit
---

# 🌟 治愈系记录助手 - SoulMate AI Companion

一个温暖、治愈的 AI 陪伴应用，帮助你记录心情、捕捉灵感、管理待办。

## ✨ 核心特性

- 🎤 **语音/文字快速记录** - 自动分类保存
- 🤖 **AI 语义解析** - 智能提取情绪、灵感和待办
- 💬 **AI 对话陪伴（RAG）** - 基于历史记录的个性化对话
- 🖼️ **AI 形象定制** - 生成专属治愈系角色（720 种组合）
- 🫧 **物理引擎心情池** - 基于 Matter.js 的动态气泡可视化

## 🚀 快速开始

### 在线使用

直接访问本 Space 即可使用完整功能！

### 配置 API 密钥

在 Space 的 **Settings → Repository secrets** 中配置：

**必需：**
- `ZHIPU_API_KEY` - 智谱 AI API 密钥
  - 获取地址：https://open.bigmodel.cn/
  - 用途：语音识别、语义解析、AI 对话

**可选：**
- `MINIMAX_API_KEY` - MiniMax API 密钥
- `MINIMAX_GROUP_ID` - MiniMax Group ID
  - 获取地址：https://platform.minimaxi.com/
  - 用途：AI 形象生成

## 📖 使用说明

1. **首页快速记录**
   - 点击麦克风录音或在输入框输入文字
   - AI 自动分析并分类保存

2. **查看分类数据**
   - 点击顶部心情、灵感、待办图标
   - 查看不同类型的记录

3. **与 AI 对话**
   - 点击 AI 形象显示问候对话框
   - 点击对话框中的聊天图标进入完整对话
   - AI 基于你的历史记录提供个性化回复

4. **定制 AI 形象**
   - 点击右下角 ✨ 按钮
   - 选择颜色、性格、外观、角色
   - 生成专属形象（需要 MiniMax API）

5. **心情气泡池**
   - 点击顶部心情图标
   - 左右滑动查看不同日期的心情卡片
   - 点击卡片展开查看当天的气泡池
   - 可以拖拽气泡，感受物理引擎效果

## 📊 API 端点

- `POST /api/process` - 处理文本/语音输入
- `POST /api/chat` - 与 AI 对话（RAG）
- `GET /api/records` - 获取所有记录
- `GET /api/moods` - 获取情绪数据
- `GET /api/inspirations` - 获取灵感
- `GET /api/todos` - 获取待办事项
- `POST /api/character/generate` - 生成角色形象
- `GET /health` - 健康检查
- `GET /docs` - API 文档

## 🔗 相关链接

- [GitHub 仓库](https://github.com/kernel-14/Nora)
- [详细文档](https://github.com/kernel-14/Nora/blob/main/README.md)
- [智谱 AI](https://open.bigmodel.cn/)
- [MiniMax](https://platform.minimaxi.com/)

## 📝 技术栈

- **后端**: FastAPI + Python 3.11
- **前端**: React + TypeScript + Vite
- **物理引擎**: Matter.js
- **AI 服务**: 智谱 AI (GLM-4) + MiniMax
- **部署**: Hugging Face Spaces (Docker)

## 🔧 本地开发

### 启动后端服务

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制 .env.example 为 .env 并填写）
cp .env.example .env

# 启动服务（端口 8000）
python scripts/start_local.py
```

### 构建前端

```bash
cd frontend
npm install
npm run build
```

### 局域网访问

1. 启动后端后，会显示局域网访问地址（如 `http://192.168.1.100:8000/`）
2. 其他设备连接同一 WiFi 后，使用该地址访问
3. 如果无法访问，请参考 [局域网访问快速修复指南](docs/局域网访问快速修复.md)

**快速诊断**：
```bash
# Windows
scripts\test_lan_access.bat

# 或访问诊断页面
http://你的IP:8000/test-connection.html
```

## 🐛 故障排查

### 问题：其他设备访问显示 "Load failed"

**原因**：防火墙阻止、网络隔离或 API 地址配置错误

**解决方案**：
1. 运行诊断工具：`scripts\test_lan_access.bat`
2. 访问诊断页面：`http://你的IP:8000/test-connection.html`
3. 查看详细指南：[局域网访问快速修复](docs/局域网访问快速修复.md)

### 问题：语音识别失败

**原因**：未配置 ZHIPU_API_KEY 或 API 配额不足

**解决方案**：
1. 检查 `.env` 文件中的 `ZHIPU_API_KEY`
2. 访问 https://open.bigmodel.cn/ 检查配额

### 问题：AI 形象生成失败

**原因**：未配置 MINIMAX_API_KEY 或 API 配额不足

**解决方案**：
1. 检查 `.env` 文件中的 `MINIMAX_API_KEY` 和 `MINIMAX_GROUP_ID`
2. 访问 https://platform.minimaxi.com/ 检查配额

## 📚 文档

- [功能架构图](docs/功能架构图.md)
- [API 配置说明](docs/API_配置说明.md)
- [局域网访问指南](docs/局域网访问指南.md)
- [局域网访问快速修复](docs/局域网访问快速修复.md)
- [心情气泡池功能说明](docs/心情气泡池功能说明.md)

## 📄 License

MIT License
