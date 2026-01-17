# Requirements Document

## Introduction

这是一个治愈系记录助手的后端核心模块。系统接收语音录音或文字输入，通过智谱 API 进行语音转写和语义解析，输出包含情绪、灵感、待办的结构化 JSON 数据，并持久化到本地文件系统。

## Glossary

- **System**: 治愈系记录助手后端系统
- **ASR_Service**: 智谱 API 语音识别服务
- **Semantic_Parser**: GLM-4-Flash 语义解析引擎
- **Storage_Manager**: 本地 JSON 文件存储管理器
- **Record**: 用户输入的单次记录（语音或文字）
- **Mood**: 情绪数据结构（type, intensity, keywords）
- **Inspiration**: 灵感数据结构（core_idea, tags, category）
- **Todo**: 待办事项数据结构（task, time, location, status）

## Requirements

### Requirement 1: 接收用户输入

**User Story:** 作为用户，我想要提交语音录音或文字内容，以便系统能够处理我的记录。

#### Acceptance Criteria

1. WHEN 用户提交音频文件，THE System SHALL 接受常见音频格式（mp3, wav, m4a）
2. WHEN 用户提交文字内容，THE System SHALL 接受 UTF-8 编码的文本字符串
3. WHEN 输入数据为空或格式无效，THE System SHALL 返回明确的错误信息
4. WHEN 音频文件大小超过 10MB，THE System SHALL 拒绝处理并返回文件过大错误

### Requirement 2: 语音转文字

**User Story:** 作为用户，我想要系统将我的语音录音转换为文字，以便进行后续的语义分析。

#### Acceptance Criteria

1. WHEN 接收到音频文件，THE ASR_Service SHALL 调用智谱 ASR API 进行语音识别
2. WHEN 语音识别成功，THE ASR_Service SHALL 返回转写后的文本内容
3. IF 智谱 API 调用失败，THEN THE System SHALL 记录错误日志并返回转写失败错误
4. WHEN 音频内容无法识别，THE ASR_Service SHALL 返回空文本并标记为识别失败

### Requirement 3: 语义解析

**User Story:** 作为用户，我想要系统从我的文本中提取情绪、灵感和待办事项，以便获得结构化的记录数据。

#### Acceptance Criteria

1. WHEN 接收到文本内容，THE Semantic_Parser SHALL 调用 GLM-4-Flash API 进行语义解析
2. WHEN 调用 GLM-4-Flash，THE System SHALL 使用指定的 System Prompt："你是一个数据转换器。请将文本解析为 JSON 格式。维度包括：1.情绪(type,intensity,keywords); 2.灵感(core_idea,tags,category); 3.待办(task,time,location)。必须严格遵循 JSON 格式返回。"
3. WHEN 解析成功，THE Semantic_Parser SHALL 返回包含 mood、inspirations、todos 的 JSON 结构
4. WHEN 文本中不包含某个维度的信息，THE Semantic_Parser SHALL 返回该维度的空值或空数组
5. IF GLM-4-Flash API 调用失败，THEN THE System SHALL 记录错误日志并返回解析失败错误

### Requirement 4: 情绪数据提取

**User Story:** 作为用户，我想要系统识别我的情绪状态，以便追踪我的情绪变化。

#### Acceptance Criteria

1. WHEN 解析情绪数据，THE Semantic_Parser SHALL 提取情绪类型（type）
2. WHEN 解析情绪数据，THE Semantic_Parser SHALL 提取情绪强度（intensity），范围为 1-10 的整数
3. WHEN 解析情绪数据，THE Semantic_Parser SHALL 提取情绪关键词（keywords），以字符串数组形式返回
4. WHEN 文本中不包含明确的情绪信息，THE Semantic_Parser SHALL 返回 null 或默认值

### Requirement 5: 灵感数据提取

**User Story:** 作为用户，我想要系统捕捉我的灵感想法，以便日后回顾和整理。

#### Acceptance Criteria

1. WHEN 解析灵感数据，THE Semantic_Parser SHALL 提取核心观点（core_idea），长度不超过 20 个字符
2. WHEN 解析灵感数据，THE Semantic_Parser SHALL 提取标签（tags），以字符串数组形式返回，最多 5 个标签
3. WHEN 解析灵感数据，THE Semantic_Parser SHALL 提取分类（category），值为"工作"、"生活"、"学习"或"创意"之一
4. WHEN 文本中包含多个灵感，THE Semantic_Parser SHALL 返回灵感数组
5. WHEN 文本中不包含灵感信息，THE Semantic_Parser SHALL 返回空数组

### Requirement 6: 待办事项提取

**User Story:** 作为用户，我想要系统识别我提到的待办事项，以便自动创建任务清单。

#### Acceptance Criteria

1. WHEN 解析待办数据，THE Semantic_Parser SHALL 提取任务描述（task）
2. WHEN 解析待办数据，THE Semantic_Parser SHALL 提取时间信息（time），保留原始表达（如"明晚"、"下周三"）
3. WHEN 解析待办数据，THE Semantic_Parser SHALL 提取地点信息（location）
4. WHEN 创建新待办事项，THE System SHALL 设置状态（status）为"pending"
5. WHEN 文本中包含多个待办事项，THE Semantic_Parser SHALL 返回待办数组
6. WHEN 文本中不包含待办信息，THE Semantic_Parser SHALL 返回空数组

### Requirement 7: 数据持久化

**User Story:** 作为用户，我想要系统保存我的记录数据，以便日后查询和分析。

#### Acceptance Criteria

1. WHEN 解析完成后，THE Storage_Manager SHALL 将完整记录保存到 records.json 文件
2. WHEN 提取到情绪数据，THE Storage_Manager SHALL 将情绪信息追加到 moods.json 文件
3. WHEN 提取到灵感数据，THE Storage_Manager SHALL 将灵感信息追加到 inspirations.json 文件
4. WHEN 提取到待办数据，THE Storage_Manager SHALL 将待办信息追加到 todos.json 文件
5. WHEN JSON 文件不存在，THE Storage_Manager SHALL 创建新文件并初始化为空数组
6. WHEN 写入文件失败，THE System SHALL 记录错误日志并返回存储失败错误
7. WHEN 保存记录时，THE System SHALL 为每条记录生成唯一 ID 和时间戳

### Requirement 8: API 接口设计

**User Story:** 作为前端开发者，我想要调用清晰的 REST API，以便集成后端功能。

#### Acceptance Criteria

1. THE System SHALL 提供 POST /api/process 接口接收用户输入
2. WHEN 请求包含音频文件，THE System SHALL 接受 multipart/form-data 格式
3. WHEN 请求包含文字内容，THE System SHALL 接受 application/json 格式
4. WHEN 处理成功，THE System SHALL 返回 HTTP 200 状态码和结构化 JSON 响应
5. WHEN 处理失败，THE System SHALL 返回适当的 HTTP 错误状态码（400/500）和错误信息
6. THE System SHALL 在响应中包含 record_id 和 timestamp 字段

### Requirement 9: 错误处理

**User Story:** 作为用户，我想要在系统出错时获得清晰的错误提示，以便了解问题所在。

#### Acceptance Criteria

1. WHEN 任何步骤发生错误，THE System SHALL 返回包含 error 字段的 JSON 响应
2. WHEN 智谱 API 调用失败，THE System SHALL 返回"语音识别服务不可用"或"语义解析服务不可用"错误
3. WHEN 输入验证失败，THE System SHALL 返回具体的验证错误信息
4. WHEN 文件操作失败，THE System SHALL 返回"数据存储失败"错误
5. THE System SHALL 记录所有错误到日志文件，包含时间戳和错误堆栈

### Requirement 10: 配置管理

**User Story:** 作为系统管理员，我想要配置 API 密钥和系统参数，以便灵活部署系统。

#### Acceptance Criteria

1. THE System SHALL 从环境变量或配置文件读取智谱 API 密钥
2. THE System SHALL 支持配置数据文件存储路径
3. THE System SHALL 支持配置音频文件大小限制
4. WHEN 必需的配置项缺失，THE System SHALL 在启动时报错并拒绝启动
5. THE System SHALL 不在日志中输出敏感信息（如 API 密钥）
