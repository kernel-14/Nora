# Design Document: Voice Text Processor

## Overview

本系统是一个基于 FastAPI 的 REST API 服务，用于处理用户的语音录音或文字输入，通过智谱 API 进行语音识别和语义解析，提取情绪、灵感和待办事项等结构化数据，并持久化到本地 JSON 文件。

系统采用分层架构设计：
- **API 层**：FastAPI 路由和请求处理
- **服务层**：业务逻辑处理（ASR、语义解析）
- **存储层**：JSON 文件持久化

核心工作流程：
1. 接收用户输入（音频文件或文本）
2. 如果是音频，调用智谱 ASR API 转写为文本
3. 调用 GLM-4-Flash API 进行语义解析
4. 提取情绪、灵感、待办数据
5. 持久化到对应的 JSON 文件
6. 返回结构化响应

## Architecture

系统采用三层架构：

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │
│  - POST /api/process                │
│  - Request validation               │
│  - Response formatting              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Service Layer               │
│  - ASRService                       │
│  - SemanticParserService            │
│  - StorageService                   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         External Services           │
│  - Zhipu ASR API                    │
│  - GLM-4-Flash API                  │
│  - Local JSON Files                 │
└─────────────────────────────────────┘
```

### 模块职责

**API Layer**:
- 处理 HTTP 请求和响应
- 输入验证（文件格式、大小、文本编码）
- 错误处理和状态码映射
- 请求日志记录

**Service Layer**:
- `ASRService`: 封装智谱 ASR API 调用，处理音频转文字
- `SemanticParserService`: 封装 GLM-4-Flash API 调用，执行语义解析
- `StorageService`: 管理 JSON 文件读写，生成唯一 ID 和时间戳

**Configuration**:
- 环境变量管理（API 密钥、文件路径、大小限制）
- 启动时配置验证

## Components and Interfaces

### 1. API Endpoint

```python
@app.post("/api/process")
async def process_input(
    audio: Optional[UploadFile] = File(None),
    text: Optional[str] = Body(None)
) -> ProcessResponse
```

**输入**:
- `audio`: 音频文件（multipart/form-data），支持 mp3, wav, m4a
- `text`: 文本内容（application/json），UTF-8 编码

**输出**:
```python
class ProcessResponse(BaseModel):
    record_id: str
    timestamp: str
    mood: Optional[MoodData]
    inspirations: List[InspirationData]
    todos: List[TodoData]
    error: Optional[str]
```

### 2. ASRService

```python
class ASRService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient()
    
    async def transcribe(self, audio_file: bytes) -> str:
        """
        调用智谱 ASR API 进行语音识别
        
        参数:
            audio_file: 音频文件字节流
        
        返回:
            转写后的文本内容
        
        异常:
            ASRServiceError: API 调用失败或识别失败
        """
```

### 3. SemanticParserService

```python
class SemanticParserService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient()
        self.system_prompt = (
            "你是一个数据转换器。请将文本解析为 JSON 格式。"
            "维度包括：1.情绪(type,intensity,keywords); "
            "2.灵感(core_idea,tags,category); "
            "3.待办(task,time,location)。"
            "必须严格遵循 JSON 格式返回。"
        )
    
    async def parse(self, text: str) -> ParsedData:
        """
        调用 GLM-4-Flash API 进行语义解析
        
        参数:
            text: 待解析的文本内容
        
        返回:
            ParsedData 对象，包含 mood, inspirations, todos
        
        异常:
            SemanticParserError: API 调用失败或解析失败
        """
```

### 4. StorageService

```python
class StorageService:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.records_file = self.data_dir / "records.json"
        self.moods_file = self.data_dir / "moods.json"
        self.inspirations_file = self.data_dir / "inspirations.json"
        self.todos_file = self.data_dir / "todos.json"
    
    def save_record(self, record: RecordData) -> str:
        """
        保存完整记录到 records.json
        
        参数:
            record: 记录数据对象
        
        返回:
            生成的唯一 record_id
        
        异常:
            StorageError: 文件写入失败
        """
    
    def append_mood(self, mood: MoodData, record_id: str) -> None:
        """追加情绪数据到 moods.json"""
    
    def append_inspirations(self, inspirations: List[InspirationData], record_id: str) -> None:
        """追加灵感数据到 inspirations.json"""
    
    def append_todos(self, todos: List[TodoData], record_id: str) -> None:
        """追加待办数据到 todos.json"""
```

## Data Models

### 核心数据结构

```python
class MoodData(BaseModel):
    type: Optional[str] = None
    intensity: Optional[int] = Field(None, ge=1, le=10)
    keywords: List[str] = []

class InspirationData(BaseModel):
    core_idea: str = Field(..., max_length=20)
    tags: List[str] = Field(default_factory=list, max_items=5)
    category: Literal["工作", "生活", "学习", "创意"]

class TodoData(BaseModel):
    task: str
    time: Optional[str] = None
    location: Optional[str] = None
    status: str = "pending"

class ParsedData(BaseModel):
    mood: Optional[MoodData] = None
    inspirations: List[InspirationData] = []
    todos: List[TodoData] = []

class RecordData(BaseModel):
    record_id: str
    timestamp: str
    input_type: Literal["audio", "text"]
    original_text: str
    parsed_data: ParsedData
```

### 存储格式

**records.json**:
```json
[
  {
    "record_id": "uuid-string",
    "timestamp": "2024-01-01T12:00:00Z",
    "input_type": "audio",
    "original_text": "转写后的文本",
    "parsed_data": {
      "mood": {...},
      "inspirations": [...],
      "todos": [...]
    }
  }
]
```

**moods.json**:
```json
[
  {
    "record_id": "uuid-string",
    "timestamp": "2024-01-01T12:00:00Z",
    "type": "开心",
    "intensity": 8,
    "keywords": ["愉快", "放松"]
  }
]
```

**inspirations.json**:
```json
[
  {
    "record_id": "uuid-string",
    "timestamp": "2024-01-01T12:00:00Z",
    "core_idea": "新的项目想法",
    "tags": ["创新", "技术"],
    "category": "工作"
  }
]
```

**todos.json**:
```json
[
  {
    "record_id": "uuid-string",
    "timestamp": "2024-01-01T12:00:00Z",
    "task": "完成报告",
    "time": "明天下午",
    "location": "办公室",
    "status": "pending"
  }
]
```


## Correctness Properties

属性（Property）是关于系统行为的特征或规则，应该在所有有效执行中保持为真。属性是人类可读规范和机器可验证正确性保证之间的桥梁。

### Property 1: 音频格式验证
*For any* 提交的文件，如果文件扩展名是 mp3、wav 或 m4a，系统应该接受该文件；如果是其他格式，系统应该拒绝并返回错误。
**Validates: Requirements 1.1**

### Property 2: UTF-8 文本接受
*For any* UTF-8 编码的文本字符串（包括中文、emoji、特殊字符），系统应该正确接受并处理。
**Validates: Requirements 1.2**

### Property 3: 无效输入错误处理
*For any* 空输入或格式无效的输入，系统应该返回包含 error 字段的 JSON 响应，而不是崩溃或返回成功状态。
**Validates: Requirements 1.3, 9.1**

### Property 4: 解析结果结构完整性
*For any* 成功的语义解析结果，返回的 JSON 应该包含 mood、inspirations、todos 三个字段，即使某些字段为空值或空数组。
**Validates: Requirements 3.3**

### Property 5: 缺失维度处理
*For any* 不包含特定维度信息的文本，解析结果中该维度应该返回 null（对于 mood）或空数组（对于 inspirations 和 todos）。
**Validates: Requirements 3.4**

### Property 6: 情绪数据结构验证
*For any* 解析出的情绪数据，应该包含 type（字符串）、intensity（1-10 的整数）、keywords（字符串数组）三个字段，且 intensity 必须在有效范围内。
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 7: 灵感数据结构验证
*For any* 解析出的灵感数据，应该包含 core_idea（长度 ≤ 20）、tags（数组长度 ≤ 5）、category（枚举值：工作/生活/学习/创意）三个字段，且所有约束都被满足。
**Validates: Requirements 5.1, 5.2, 5.3**

### Property 8: 待办数据结构验证
*For any* 解析出的待办数据，应该包含 task（必需）、time（可选）、location（可选）、status（默认为 "pending"）四个字段。
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### Property 9: 数据持久化完整性
*For any* 成功处理的记录，应该在 records.json 中保存完整记录，并且如果包含情绪/灵感/待办数据，应该同时追加到对应的 moods.json、inspirations.json、todos.json 文件中。
**Validates: Requirements 7.1, 7.2, 7.3, 7.4**

### Property 10: 文件初始化
*For any* 不存在的 JSON 文件，当首次写入时，系统应该创建该文件并初始化为空数组 `[]`。
**Validates: Requirements 7.5**

### Property 11: 唯一 ID 生成
*For any* 两条不同的记录，生成的 record_id 应该是唯一的（不重复）。
**Validates: Requirements 7.7**

### Property 12: 成功响应格式
*For any* 成功处理的请求，HTTP 响应应该返回 200 状态码，并且响应 JSON 包含 record_id、timestamp、mood、inspirations、todos 字段。
**Validates: Requirements 8.4, 8.6**

### Property 13: 错误响应格式
*For any* 处理失败的请求，HTTP 响应应该返回适当的错误状态码（400 或 500），并且响应 JSON 包含 error 字段，描述具体错误信息。
**Validates: Requirements 8.5, 9.1, 9.3**

### Property 14: 错误日志记录
*For any* 系统发生的错误，应该在日志文件中记录该错误，包含时间戳和错误堆栈信息。
**Validates: Requirements 9.5**

### Property 15: 敏感信息保护
*For any* 日志输出，不应该包含敏感信息（如 API 密钥、用户密码等）。
**Validates: Requirements 10.5**

## Error Handling

### 错误分类

**1. 输入验证错误（HTTP 400）**:
- 音频文件格式不支持
- 音频文件大小超过限制
- 文本内容为空
- 请求格式错误（既没有 audio 也没有 text）

**2. 外部服务错误（HTTP 500）**:
- 智谱 ASR API 调用失败
- GLM-4-Flash API 调用失败
- API 返回非预期格式

**3. 存储错误（HTTP 500）**:
- JSON 文件写入失败
- 磁盘空间不足
- 文件权限错误

**4. 配置错误（启动时失败）**:
- API 密钥缺失
- 数据目录不可访问
- 必需配置项缺失

### 错误处理策略

```python
class APIError(Exception):
    """API 层错误基类"""
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code

class ASRServiceError(APIError):
    """ASR 服务错误"""
    def __init__(self, message: str = "语音识别服务不可用"):
        super().__init__(message, 500)

class SemanticParserError(APIError):
    """语义解析服务错误"""
    def __init__(self, message: str = "语义解析服务不可用"):
        super().__init__(message, 500)

class StorageError(APIError):
    """存储错误"""
    def __init__(self, message: str = "数据存储失败"):
        super().__init__(message, 500)

class ValidationError(APIError):
    """输入验证错误"""
    def __init__(self, message: str):
        super().__init__(message, 400)
```

### 错误响应格式

```json
{
  "error": "具体错误描述",
  "detail": "详细错误信息（可选）",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 日志记录

使用 Python logging 模块：
- **INFO**: 正常请求处理流程
- **WARNING**: 可恢复的异常情况（如 API 重试）
- **ERROR**: 错误情况，包含完整堆栈信息
- **DEBUG**: 详细调试信息（开发环境）

日志格式：
```
[2024-01-01 12:00:00] [ERROR] [request_id: xxx] ASR API call failed: Connection timeout
Traceback: ...
```

## Testing Strategy

本系统采用双重测试策略：单元测试和基于属性的测试（Property-Based Testing）。

### 单元测试

单元测试用于验证特定示例、边缘情况和错误条件：

**测试范围**:
- API 端点的请求/响应处理
- 各服务类的 mock 测试（模拟外部 API）
- 数据模型的验证逻辑
- 错误处理流程
- 配置加载和验证

**示例测试用例**:
- 测试 POST /api/process 端点存在
- 测试接受 multipart/form-data 格式
- 测试接受 application/json 格式
- 测试 ASR API 调用失败时的错误处理
- 测试 GLM-4-Flash API 调用失败时的错误处理
- 测试文件写入失败时的错误处理
- 测试配置缺失时启动失败
- 测试空音频识别的边缘情况
- 测试无情绪信息文本的边缘情况
- 测试无灵感信息文本的边缘情况
- 测试无待办信息文本的边缘情况

### 基于属性的测试（Property-Based Testing）

基于属性的测试用于验证通用属性在所有输入下都成立。

**测试库**: 使用 `hypothesis` 库（Python 的 PBT 框架）

**配置**:
- 每个属性测试运行最少 100 次迭代
- 每个测试必须引用设计文档中的属性编号
- 标签格式：`# Feature: voice-text-processor, Property N: [property text]`

**属性测试覆盖**:
- Property 1: 音频格式验证
- Property 2: UTF-8 文本接受
- Property 3: 无效输入错误处理
- Property 4: 解析结果结构完整性
- Property 5: 缺失维度处理
- Property 6: 情绪数据结构验证
- Property 7: 灵感数据结构验证
- Property 8: 待办数据结构验证
- Property 9: 数据持久化完整性
- Property 10: 文件初始化
- Property 11: 唯一 ID 生成
- Property 12: 成功响应格式
- Property 13: 错误响应格式
- Property 14: 错误日志记录
- Property 15: 敏感信息保护

**测试策略**:
- 使用 hypothesis 生成随机输入（文件名、文本、数据结构）
- 使用 pytest-mock 模拟外部 API 调用
- 使用临时文件系统进行存储测试
- 验证所有属性在随机输入下都成立

**示例属性测试**:
```python
from hypothesis import given, strategies as st
import pytest

@given(st.text(min_size=1))
def test_property_2_utf8_text_acceptance(text):
    """
    Feature: voice-text-processor, Property 2: UTF-8 文本接受
    For any UTF-8 encoded text string, the system should accept and process it.
    """
    response = client.post("/api/process", json={"text": text})
    assert response.status_code in [200, 500]  # 接受输入，可能解析失败但不应拒绝

@given(st.lists(st.text(), min_size=1, max_size=10))
def test_property_11_unique_id_generation(texts):
    """
    Feature: voice-text-processor, Property 11: 唯一 ID 生成
    For any two different records, the generated record_ids should be unique.
    """
    record_ids = []
    for text in texts:
        response = client.post("/api/process", json={"text": text})
        if response.status_code == 200:
            record_ids.append(response.json()["record_id"])
    
    # 所有 ID 应该唯一
    assert len(record_ids) == len(set(record_ids))
```

### 测试覆盖目标

- 代码覆盖率：≥ 80%
- 属性测试：覆盖所有 15 个正确性属性
- 单元测试：覆盖所有边缘情况和错误路径
- 集成测试：端到端流程测试（音频 → 转写 → 解析 → 存储）

