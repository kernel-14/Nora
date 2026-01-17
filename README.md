# Voice Text Processor

治愈系记录助手后端核心模块 - 语音和文本处理服务

## 项目简介

这是一个基于 FastAPI 的 REST API 服务，用于处理用户的语音录音或文字输入，通过智谱 API 进行语音识别和语义解析，提取情绪、灵感和待办事项等结构化数据，并持久化到本地 JSON 文件。

## 功能特性

- 🎤 **语音转文字**: 支持 mp3, wav, m4a 格式的音频文件转写
- 📝 **文本处理**: 直接接受文本输入进行语义分析
- 😊 **情绪识别**: 提取情绪类型、强度和关键词
- 💡 **灵感捕捉**: 识别核心观点、标签和分类
- ✅ **待办提取**: 自动识别任务、时间和地点信息
- 💾 **数据持久化**: 结构化数据保存到本地 JSON 文件
- 🔒 **安全日志**: 自动过滤敏感信息（API 密钥等）

## 项目结构

```
voice-text-processor/
├── app/                    # 应用代码
│   ├── __init__.py
│   ├── main.py            # FastAPI 应用入口
│   ├── config.py          # 配置管理
│   └── logging_config.py  # 日志配置
├── tests/                 # 测试代码
│   └── __init__.py
├── data/                  # 数据存储目录
│   └── .gitkeep
├── logs/                  # 日志目录（自动创建）
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量示例
├── .gitignore
└── README.md
```

## 快速开始

### 1. 环境要求

- Python 3.9+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 到 `.env` 并填入你的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，至少需要设置：

```
ZHIPU_API_KEY=your_actual_api_key_here
```

### 4. 运行应用

```bash
python -m app.main
```

或使用 uvicorn：

```bash
uvicorn app.main:app --reload
```

应用将在 `http://localhost:8000` 启动。

### 5. 访问 API 文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 配置说明

所有配置通过环境变量设置：

| 环境变量 | 必需 | 默认值 | 说明 |
|---------|------|--------|------|
| `ZHIPU_API_KEY` | ✅ | - | 智谱 AI API 密钥 |
| `DATA_DIR` | ❌ | `data` | 数据存储目录 |
| `MAX_AUDIO_SIZE` | ❌ | `10485760` (10MB) | 最大音频文件大小（字节） |
| `LOG_LEVEL` | ❌ | `INFO` | 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| `LOG_FILE` | ❌ | `logs/app.log` | 日志文件路径 |
| `HOST` | ❌ | `0.0.0.0` | 服务器主机 |
| `PORT` | ❌ | `8000` | 服务器端口 |

## 启动验证

应用启动时会自动验证配置：

- ✅ 检查必需的环境变量（ZHIPU_API_KEY）
- ✅ 验证数据目录可写
- ✅ 验证日志目录可写
- ✅ 验证 API 密钥格式

如果配置无效，应用将拒绝启动并显示错误信息。

## 日志系统

日志系统特性：

- 📋 **格式化输出**: 包含时间戳、级别、模块名和消息
- 📁 **文件输出**: 同时输出到控制台和文件
- 🔒 **敏感信息过滤**: 自动屏蔽 API 密钥、密码等敏感数据
- 📊 **错误追踪**: 错误日志包含完整堆栈信息

日志格式示例：
```
[2024-01-01 12:00:00] [INFO] [app.main] Application startup complete
[2024-01-01 12:00:01] [ERROR] [app.services.asr] ASR API call failed: Connection timeout
```

## 健康检查

访问 `/health` 端点检查服务状态：

```bash
curl http://localhost:8000/health
```

响应示例：
```json
{
  "status": "healthy",
  "data_dir": "data",
  "max_audio_size": 10485760
}
```

## 开发

### 运行测试

```bash
pytest
```

### 代码覆盖率

```bash
pytest --cov=app --cov-report=html
```

### 代码格式化

```bash
black app/ tests/
```

### 类型检查

```bash
mypy app/
```

## 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **Pydantic**: 数据验证和设置管理
- **httpx**: 异步 HTTP 客户端
- **uvicorn**: ASGI 服务器
- **pytest**: 测试框架
- **hypothesis**: 基于属性的测试

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。
