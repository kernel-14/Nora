# 治愈系记录助手 - SoulMate AI Companion

一个温暖、治愈的 AI 陪伴应用，帮助你记录心情、捕捉灵感、管理待办，并随时与 AI 助手对话。

## 🌟 核心特性

- 🎨 **精美 WebUI** - React + TypeScript 构建的现代化界面
- 🎤 **首页快速记录** - 语音/文字快速记录，自动分类保存
- 🤖 **AI 语义解析** - 智能提取情绪、灵感和待办事项
- 💬 **AI 对话陪伴（RAG）** - 基于历史记录的个性化对话
- 🖼️ **AI 形象定制** - 生成专属的治愈系猫咪角色（720 种组合）
- 💾 **本地存储** - 数据和图片安全保存在本地

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 1. 安装依赖

```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
cd ..
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# 必需：智谱 AI API 密钥（用于语义解析和对话）
ZHIPU_API_KEY=your_zhipu_api_key_here

# 可选：MiniMax API（用于生成角色形象）
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_GROUP_ID=your_minimax_group_id_here

# 可选：服务配置
DATA_DIR=data
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
MAX_AUDIO_SIZE=10485760
```

**获取 API 密钥：**
- 智谱 AI: https://open.bigmodel.cn/
- MiniMax: https://platform.minimaxi.com/

前端配置 `frontend/.env.local`：
```bash
VITE_API_URL=http://localhost:8000
```

### 3. 启动服务

**方式 1：一键启动（推荐）**

同时启动前后端：
```bash
# Windows CMD
start_dev.bat

# PowerShell
.\start_dev.ps1
```

**方式 2：分别启动**

终端 1 - 启动后端：
```bash
# Windows CMD
启动后端.bat

# PowerShell
.\启动后端.ps1
```

终端 2 - 启动前端：
```bash
# Windows CMD
启动前端.bat

# PowerShell
.\启动前端.ps1
```

**方式 3：手动启动**

终端 1 - 启动后端：
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

终端 2 - 启动前端：
```bash
cd frontend
npm run dev
```

> **注意：** 必须在项目根目录运行后端命令，不能在 `app/` 目录内。如遇到 `ModuleNotFoundError`，请运行 `python 诊断环境.py` 检查环境。
> 
> **启动脚本说明：** 详见 [启动脚本说明.md](启动脚本说明.md)

### 4. 访问应用

- 🌐 **前端界面**: http://localhost:5173
- 🔧 **后端 API**: http://localhost:8000
- 📚 **API 文档**: http://localhost:8000/docs

## 🎯 核心功能

### 1. 首页快速记录

在首页通过语音或文字快速记录想法，系统自动分析并分类保存。

**两种输入方式：**
- 🎤 **语音录制** - 点击麦克风按钮，说出你的想法（自动转换 webm → wav）
- ⌨️ **文字输入** - 在输入框中直接打字

**工作流程：**
```
用户输入 → /api/process → AI 分析 → 保存到 records.json → 自动拆分到：
  - moods.json (情绪)
  - inspirations.json (灵感)
  - todos.json (待办)
```

**特点：**
- ✨ 一键记录，无需多步操作
- 🚀 实时处理和反馈（3-5 秒）
- 💾 自动保存和分类
- 🎯 支持所有现代浏览器

### 2. AI 对话陪伴（RAG 增强）

与智能形象交流时，AI 会基于你的历史记录提供个性化回复。

**对话特点：**
- 💬 每条消息调用 `/api/chat` 接口
- 🧠 使用 RAG（检索增强生成）技术
- 📚 基于 `records.json` 作为知识库（最近 10 条）
- 💝 提供个性化、有温度的回复

**使用场景：**
- 💭 倾诉心情，获得情感支持
- 🤔 讨论想法，获得建议
- 📝 回顾过往，获得洞察
- 🌟 日常陪伴，温暖治愈

**功能对比：**

| 功能 | 首页记录 | AI 对话 |
|------|---------|---------|
| 目的 | 快速记录想法 | 智能对话陪伴 |
| API | `/api/process` | `/api/chat` |
| 调用 | 一次性处理 | 每条消息 |
| 知识库 | 不使用 | 使用 RAG |
| 输出 | 结构化数据 | 自然语言 |
| 保存 | 自动保存 | 不保存对话 |

### 3. 智能语义解析

输入文本或语音，AI 自动提取：
- **情绪** - 类型、强度（1-10）、关键词
- **灵感** - 核心观点、标签、分类
- **待办** - 任务、时间、地点

**示例：**
```
输入："今天工作很累，但看到晚霞很美。明天要整理项目文档。"

输出：
- 情绪: 疲惫 (强度: 7)
- 灵感: 晚霞的美好
- 待办: 整理项目文档 (明天)
```

### 4. AI 形象定制

生成专属的治愈系猫咪 AI 陪伴形象：

**定制选项：**
- 🎨 **8 种颜色** - 温暖粉、天空蓝、薄荷绿、奶油黄、薰衣草紫、珊瑚橙、纯白、浅灰
- 😊 **6 种性格** - 活泼、温柔、聪明、慵懒、勇敢、害羞
- 👓 **5 种外观** - 戴眼镜、戴帽子、戴围巾、戴蝴蝶结、无配饰
- 🎭 **3 种角色** - 陪伴式朋友、温柔照顾型长辈、引导型老师

**使用方法：**
1. 点击主页右下角 ✨ 按钮
2. 选择偏好（两步流程）
3. 点击"生成形象"
4. 等待 30-60 秒
5. 查看新生成的 AI 形象

## 📁 项目结构

```
voice-text-processor/
├── app/                    # 后端代码
│   ├── main.py            # FastAPI 应用入口
│   ├── semantic_parser.py # AI 语义解析
│   ├── asr_service.py     # 语音识别
│   ├── image_service.py   # AI 图像生成
│   ├── storage.py         # 数据存储
│   ├── user_config.py     # 用户配置
│   └── models.py          # 数据模型
├── frontend/              # 前端代码
│   ├── components/        # React 组件
│   │   ├── HomeInput.tsx         # 首页输入组件
│   │   ├── AIEntity.tsx          # AI 形象
│   │   ├── ChatDialog.tsx        # 对话界面
│   │   └── ...
│   ├── services/          # API 服务层
│   └── App.tsx           # 主应用
├── data/                  # 数据存储
│   ├── records.json      # 完整记录
│   ├── moods.json        # 情绪数据
│   ├── inspirations.json # 灵感数据
│   └── todos.json        # 待办数据
├── generated_images/      # AI 生成的角色图片
├── docs/                  # 详细文档
├── tests/                # 测试代码
└── README.md
```

## 🔌 API 端点

### 核心功能

| 方法 | 端点 | 功能 |
|------|------|------|
| POST | `/api/process` | 处理文本/语音输入（首页记录） |
| POST | `/api/chat` | 与 AI 助手对话（RAG 增强） |
| GET | `/api/records` | 获取所有记录 |
| GET | `/api/moods` | 获取情绪数据 |
| GET | `/api/inspirations` | 获取灵感 |
| GET | `/api/todos` | 获取待办事项 |
| PATCH | `/api/todos/{id}` | 更新待办状态 |
| GET | `/api/user/config` | 获取用户配置 |
| POST | `/api/character/generate` | 生成角色形象 |
| GET | `/health` | 健康检查 |

### API 示例

#### 处理文本输入（首页记录）
```bash
curl -X POST http://localhost:8000/api/process \
  -F "text=今天心情很好，想到了一个新点子，明天要记得买书"
```

#### 与 AI 对话（RAG）
```bash
curl -X POST http://localhost:8000/api/chat \
  -F "text=我最近在做什么？"
```

## 🛠️ 技术栈

### 后端
- **FastAPI** - 现代化 Web 框架
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI 服务器
- **智谱 AI** - ASR 和语义解析
- **MiniMax** - 图像生成
- **httpx** - 异步 HTTP 客户端

### 前端
- **React 19** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **Lucide React** - 图标库

### 数据存储
- **JSON 文件** - 本地持久化
- **静态文件服务** - 图片访问

## 🔍 故障排查

### 常见问题

#### Q: 后端启动失败 - ModuleNotFoundError: No module named 'app'

**原因：** 在错误的目录运行命令

**解决方法：**
1. 确保在项目根目录（不是 `app/` 目录内）
2. 使用启动脚本：`启动后端.bat` 或 `.\启动后端.ps1`
3. 或手动运行：`python -m uvicorn app.main:app --reload`
4. 运行诊断：`python 诊断环境.py`

详见：[docs/后端启动问题排查.md](docs/后端启动问题排查.md)

#### Q: 语音录制不工作

**解决方法：**
1. 检查浏览器是否支持（Chrome/Edge 推荐）
2. 允许麦克风权限
3. 使用 HTTPS 或 localhost

**注意：** 浏览器录音默认使用 webm 格式，前端会自动转换为 wav 格式（约 1 秒）。

详见：[docs/语音录制问题排查.md](docs/语音录制问题排查.md)

#### Q: 前端无法连接后端

**解决方法：**
1. 检查后端是否启动: `curl http://localhost:8000/health`
2. 检查 CORS 配置
3. 检查 `VITE_API_URL` 环境变量

#### Q: AI 对话没有使用历史记录

**解决方法：**
1. 确保已经添加了一些记录
2. 问更具体的问题，如"我昨天做了什么？"
3. 检查 `data/records.json` 是否有数据

#### Q: AI 形象生成失败

**解决方法：**
1. 检查 `MINIMAX_API_KEY` 是否配置
2. 检查 API 配额是否充足
3. 查看详细错误信息

### 查看日志

```bash
# 后端日志
tail -f logs/app.log

# 或在 Windows 中
Get-Content logs/app.log -Wait
```

## 🧪 测试

### 运行测试

```bash
# 后端测试
pytest

# 环境诊断
python 诊断环境.py

# 功能测试
python test_home_input.py
```

### 测试页面

- **音频录制测试**: 打开 `test_audio_recording.html`
- **API 测试**: 访问 http://localhost:8000/docs

## ⚙️ 配置说明

### 环境变量

| 变量 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `ZHIPU_API_KEY` | ✅ | - | 智谱 AI API 密钥 |
| `MINIMAX_API_KEY` | ❌ | - | MiniMax API 密钥（图像生成） |
| `MINIMAX_GROUP_ID` | ❌ | - | MiniMax Group ID |
| `DATA_DIR` | ❌ | `data` | 数据存储目录 |
| `LOG_LEVEL` | ❌ | `INFO` | 日志级别 |
| `HOST` | ❌ | `0.0.0.0` | 服务器地址 |
| `PORT` | ❌ | `8000` | 服务器端口 |
| `MAX_AUDIO_SIZE` | ❌ | `10485760` | 最大音频文件大小 |

## 📚 详细文档

- **[功能架构图](docs/功能架构图.md)** - 系统架构和数据流向
- **[后端启动问题排查](docs/后端启动问题排查.md)** - 启动问题解决方案
- **[语音录制问题排查](docs/语音录制问题排查.md)** - 音频格式和录制问题
- **[API 文档](http://localhost:8000/docs)** - 在线 API 文档（需启动后端）
- **[PRD.md](PRD.md)** - 产品需求文档

## 🎯 使用指南

### 基本使用流程

1. **启动应用**
   ```bash
   启动后端.bat  # 或 .\启动后端.ps1
   cd frontend && npm run dev
   ```

2. **首页快速记录**
   - 点击麦克风录音或输入文字
   - AI 自动分析并保存
   - 查看"记录成功"提示

3. **查看分类数据**
   - 点击"心情"查看情绪气泡图
   - 点击"灵感"浏览灵感卡片
   - 点击"待办"管理任务列表

4. **与 AI 对话**
   - 任意页面点击对话按钮
   - AI 基于历史记录提供个性化回复

5. **定制 AI 形象**
   - 点击主页右下角 ✨ 按钮
   - 选择颜色、性格、外观、角色
   - 生成专属形象

## 🚀 部署

### 生产环境构建

**前端：**
```bash
cd frontend
npm run build
```

**后端：**
```bash
# 使用 gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🎓 开发指南

### 添加新功能

1. **后端 API** - 在 `app/main.py` 添加新端点
2. **前端组件** - 在 `frontend/components/` 创建新组件
3. **数据模型** - 在 `app/models.py` 定义数据结构

### 代码规范

- Python: PEP 8
- TypeScript: ESLint
- 提交信息: Conventional Commits

## 🔐 安全机制

### API Key 保护
- 存储在 `.env` 文件
- 不提交到版本控制
- 日志中自动过滤

### 输入验证
- 前端基本格式验证
- 后端 Pydantic 模型验证
- 文件大小和格式限制

## 🎯 未来计划

- [ ] WebSocket 实时推送
- [ ] 多轮对话历史
- [ ] 向量数据库（更好的 RAG）
- [ ] 语音合成（AI 语音回复）
- [ ] 多语言支持
- [ ] 主题切换
- [ ] 数据导出和备份

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 开发流程
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

MIT License

## 📞 联系方式

如有问题或建议，请提交 Issue。

---

**祝你使用愉快！让 AI 陪伴你的每一天 🌟**
