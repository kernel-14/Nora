---
title: SoulMate AI Companion
emoji: 🌟
colorFrom: purple
colorTo: pink
sdk: gradio
sdk_version: "4.19.2"
app_file: app.py
pinned: false
license: mit
python_version: "3.11"
---

# 🌟 治愈系记录助手 - SoulMate AI Companion

一个温暖、治愈的 AI 陪伴应用，帮助你记录心情、捕捉灵感、管理待办，并随时与 AI 助手对话。

## ✨ 核心特性

- 🎤 **语音/文字快速记录** - 自动分类保存
- 🤖 **AI 语义解析** - 智能提取情绪、灵感和待办
- 💬 **AI 对话陪伴（RAG）** - 基于历史记录的个性化对话
- 🖼️ **AI 形象定制** - 生成专属的治愈系猫咪角色
- 🫧 **物理引擎心情池** - 基于 Matter.js 的动态气泡可视化
- 💾 **本地存储** - 数据安全保存

## 🚀 快速开始

### 1. 配置 API 密钥

在 Space Settings → Repository secrets 中添加：

**必需：**
- `ZHIPU_API_KEY` - 智谱 AI API 密钥
  - 获取地址：https://open.bigmodel.cn/
  - 用途：语音识别、语义解析、AI 对话

**可选：**
- `MINIMAX_API_KEY` - MiniMax API 密钥
- `MINIMAX_GROUP_ID` - MiniMax Group ID
  - 获取地址：https://platform.minimaxi.com/
  - 用途：AI 形象生成

### 2. 使用应用

1. **首页快速记录** - 点击麦克风录音或输入文字
2. **查看分类数据** - 点击"心情"、"灵感"、"待办"
3. **与 AI 对话** - 点击 AI 形象进行对话
4. **定制 AI 形象** - 点击右下角 ✨ 按钮

## 📖 功能说明

### 首页快速记录
在首页通过语音或文字快速记录想法，系统自动分析并分类保存到：
- 📝 records.json - 完整记录
- 😊 moods.json - 情绪数据
- 💡 inspirations.json - 灵感内容
- ✅ todos.json - 待办事项

### AI 对话陪伴（RAG）
与 AI 交流时，系统会基于你的历史记录提供个性化回复：
- 使用 RAG（检索增强生成）技术
- 基于最近 10 条记录作为知识库
- 提供有温度的个性化回复

### 物理引擎心情气泡池
基于 Matter.js 的动态心情可视化：
- 真实物理碰撞效果
- 可拖拽交互
- 点击查看详情
- 30 种情绪类型

### AI 形象定制
生成专属的治愈系猫咪 AI 陪伴形象：
- 8 种颜色选择
- 6 种性格类型
- 5 种外观配饰
- 3 种角色定位

## 🛠️ 技术栈

### 后端
- FastAPI - Web 框架
- 智谱 AI - ASR 和语义解析
- MiniMax - 图像生成
- Pydantic - 数据验证

### 前端
- React 19 + TypeScript
- Vite - 构建工具
- Tailwind CSS - 样式
- Matter.js - 物理引擎

## 📊 API 端点

- `POST /api/process` - 处理文本/语音输入
- `POST /api/chat` - 与 AI 对话（RAG）
- `GET /api/records` - 获取所有记录
- `GET /api/moods` - 获取情绪数据
- `GET /api/inspirations` - 获取灵感
- `GET /api/todos` - 获取待办事项
- `POST /api/character/generate` - 生成角色形象

## 🔒 隐私说明

- 所有数据存储在 Hugging Face Space 的临时存储中
- 不会上传到外部服务器
- API 密钥安全存储在环境变量中

## 📄 许可证

MIT License

## 🔗 相关链接

- [GitHub 仓库](https://github.com/your-username/your-repo)
- [详细文档](https://github.com/your-username/your-repo/blob/main/README.md)
- [部署指南](https://github.com/your-username/your-repo/blob/main/部署指南.md)

---

**享受你的 AI 陪伴之旅！** 🎊
