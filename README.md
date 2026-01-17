# Voice Text Processor

治愈系记录助手核心模块 - AI 语义解析与数据处理

## 项目简介

这是一个 Python 核心处理模块，用于处理用户的文字输入，通过智谱 AI API 进行语义解析，自动提取情绪、灵感和待办事项等结构化数据，并持久化到本地 JSON 文件。

本模块专注于 AI 语义处理和数据存储，可以被其他应用（如 iOS 客户端）直接调用或集成。

## 功能特性

- 🤖 **AI 语义解析**: 使用智谱 GLM-4-Flash 模型进行智能文本分析
- 😊 **情绪识别**: 自动提取情绪类型、强度（1-10）和关键词
- 💡 **灵感捕捉**: 识别核心观点、自动生成标签和分类（工作/生活/学习/创意）
- ✅ **待办提取**: 智能识别任务、时间和地点信息
- 💾 **数据持久化**: 结构化数据保存到本地 JSON 文件
- 🔒 **安全日志**: 自动过滤敏感信息（API 密钥等）
- 🧪 **完整测试**: 包含单元测试、集成测试和端到端测试

## 项目结构

```
voice-text-processor/
├── app/                    # 核心应用代码
│   ├── __init__.py
│   ├── semantic_parser.py # AI 语义解析服务
│   ├── storage.py         # 数据存储服务
│   ├── models.py          # 数据模型定义
│   ├── config.py          # 配置管理
│   ├── logging_config.py  # 日志配置
│   ├── asr_service.py     # 语音识别服务（预留）
│   └── main.py            # FastAPI 入口（可选）
├── tests/                 # 测试代码
│   ├── test_semantic_parser.py
│   ├── test_storage.py
│   └── ...
├── data/                  # 数据存储目录
│   ├── records.json       # 完整记录
│   ├── moods.json         # 情绪数据
│   ├── inspirations.json  # 灵感数据
│   └── todos.json         # 待办数据
├── logs/                  # 日志目录
├── test_full_flow.py      # 完整流程测试脚本
├── requirements.txt       # Python 依赖
├── .env                   # 环境变量配置
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

在项目根目录创建 `.env` 文件：

```bash
# 必需：智谱 AI API 密钥
ZHIPU_API_KEY=your_actual_api_key_here

# 可选：数据存储目录（默认：data）
DATA_DIR=data

# 可选：日志级别（默认：INFO）
LOG_LEVEL=INFO
```

### 4. 运行测试

运行完整流程测试，验证 AI 解析和数据存储功能：

```bash
python test_full_flow.py
```

这个脚本会：
1. 测试 5 个不同场景的文本输入
2. 调用 AI 进行语义解析
3. 提取情绪、灵感和待办事项
4. 保存数据到 JSON 文件
5. 验证存储结果

### 5. 查看结果

测试完成后，查看 `data/` 目录下的 JSON 文件：
- `records.json` - 完整的记录数据
- `moods.json` - 情绪数据
- `inspirations.json` - 灵感数据
- `todos.json` - 待办数据

## 使用示例

### 直接调用 API

```python
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

from app.semantic_parser import SemanticParserService
from app.storage import StorageService
from app.models import RecordData
from datetime import datetime
import uuid

async def process_text(text: str):
    """处理文本并存储结果"""
    # 初始化服务
    api_key = os.getenv('ZHIPU_API_KEY')
    parser = SemanticParserService(api_key)
    storage = StorageService('data')
    
    try:
        # AI 语义解析
        parsed_data = await parser.parse(text)
        
        # 生成记录
        record = RecordData(
            record_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            input_type="text",
            original_text=text,
            parsed_data=parsed_data
        )
        
        # 保存数据
        storage.save_record(record)
        
        if parsed_data.mood:
            storage.append_mood(parsed_data.mood, record.record_id, record.timestamp)
        
        if parsed_data.inspirations:
            storage.append_inspirations(parsed_data.inspirations, record.record_id, record.timestamp)
        
        if parsed_data.todos:
            storage.append_todos(parsed_data.todos, record.record_id, record.timestamp)
        
        print(f"✅ 处理完成！记录 ID: {record.record_id}")
        return record
        
    finally:
        await parser.close()

# 使用示例
text = "今天工作很累，但看到晚霞很美。明天要整理项目文档。"
asyncio.run(process_text(text))
```

### 数据格式

**输入**：
```
今天工作真的好累啊，老板又临时加了三个需求，感觉压力山大。
不过下班的时候看到窗外的晚霞特别美，心情稍微好了一点。
明天记得要把项目文档整理一下，还要准备周五的汇报材料。
```

**输出**：
```json
{
  "mood": {
    "type": "焦虑",
    "intensity": 8,
    "keywords": ["压力", "疲惫", "放松"]
  },
  "inspirations": [
    {
      "core_idea": "晚霞可以缓解压力",
      "tags": ["自然", "治愈"],
      "category": "生活"
    }
  ],
  "todos": [
    {
      "task": "整理文档",
      "time": "明天",
      "location": null,
      "status": "pending"
    },
    {
      "task": "准备周五汇报材料",
      "time": "周五",
      "location": null,
      "status": "pending"
    }
  ]
}
```

## 配置说明

所有配置通过环境变量设置：

| 环境变量 | 必需 | 默认值 | 说明 |
|---------|------|--------|------|
| `ZHIPU_API_KEY` | ✅ | - | 智谱 AI API 密钥 |
| `DATA_DIR` | ❌ | `data` | 数据存储目录 |
| `LOG_LEVEL` | ❌ | `INFO` | 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| `LOG_FILE` | ❌ | `logs/app.log` | 日志文件路径 |

## 日志系统

日志系统特性：

- 📋 **格式化输出**: 包含时间戳、级别、模块名和消息
- 📁 **文件输出**: 同时输出到控制台和文件
- 🔒 **敏感信息过滤**: 自动屏蔽 API 密钥、密码等敏感数据
- 📊 **错误追踪**: 错误日志包含完整堆栈信息

日志格式示例：
```
[2026-01-17 12:00:00] [INFO] [app.semantic_parser] Semantic parsing successful
[2026-01-17 12:00:01] [ERROR] [app.semantic_parser] API call failed: Connection timeout
```

## 开发

### 运行所有测试

```bash
pytest
```

### 运行特定测试

```bash
# 测试语义解析
pytest tests/test_semantic_parser.py

# 测试数据存储
pytest tests/test_storage.py

# 端到端测试
pytest tests/test_e2e_integration.py
```

### 代码覆盖率

```bash
pytest --cov=app --cov-report=html
```

查看覆盖率报告：打开 `htmlcov/index.html`

### 代码格式化

```bash
black app/ tests/
```

### 类型检查

```bash
mypy app/
```

## 测试场景

项目包含 5 个完整的测试场景：

1. **工作压力与情绪记录** - 测试复杂情绪识别和多待办提取
2. **学习灵感与创意记录** - 测试技术灵感和分类能力
3. **日常生活与待办清单** - 测试多个时间地点的待办识别
4. **情感倾诉与心情记录** - 测试深层情感和人生感悟
5. **创意想法与项目规划** - 测试项目规划和创意识别

详见 `test_full_flow.py` 和 `模拟对话测试文档.md`

## 技术栈

- **Python 3.9+**: 核心语言
- **智谱 AI GLM-4-Flash**: AI 语义解析模型
- **Pydantic**: 数据验证和模型定义
- **httpx**: 异步 HTTP 客户端
- **pytest**: 测试框架
- **hypothesis**: 基于属性的测试
- **python-dotenv**: 环境变量管理

## 数据结构

### RecordData（完整记录）
```python
{
    "record_id": str,        # UUID
    "timestamp": str,        # ISO 8601 格式
    "input_type": str,       # "text" 或 "audio"
    "original_text": str,    # 原始文本
    "parsed_data": {         # 解析后的数据
        "mood": MoodData,
        "inspirations": List[InspirationData],
        "todos": List[TodoData]
    }
}
```

### MoodData（情绪数据）
```python
{
    "type": str,             # 情绪类型（如：焦虑、喜悦）
    "intensity": int,        # 强度 1-10
    "keywords": List[str]    # 关键词列表
}
```

### InspirationData（灵感数据）
```python
{
    "core_idea": str,        # 核心观点（20字以内）
    "tags": List[str],       # 标签列表
    "category": str          # 分类：工作/生活/学习/创意
}
```

### TodoData（待办数据）
```python
{
    "task": str,             # 任务描述
    "time": Optional[str],   # 时间信息
    "location": Optional[str], # 地点信息
    "status": str            # 状态（默认：pending）
}
```

## 常见问题

### Q: AI 没有提取出情绪/灵感/待办？
A: 这可能是因为：
1. 文本内容确实不包含相关信息
2. AI 模型的随机性导致偶尔识别失败
3. 可以尝试调整 `semantic_parser.py` 中的 `system_prompt`

### Q: 如何提高识别准确率？
A: 
1. 提供更详细、结构化的文本输入
2. 在 `semantic_parser.py` 中优化 prompt
3. 调整 temperature 和 top_p 参数

### Q: 数据存储在哪里？
A: 所有数据存储在 `data/` 目录下的 JSON 文件中：
- `records.json` - 完整记录
- `moods.json` - 情绪数据
- `inspirations.json` - 灵感数据
- `todos.json` - 待办数据

### Q: 如何集成到其他应用？
A: 可以直接导入并使用核心模块：
```python
from app.semantic_parser import SemanticParserService
from app.storage import StorageService
```

或者启动 FastAPI 服务（如果需要 HTTP API）：
```bash
python -m app.main
```

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。
