# Implementation Plan: Voice Text Processor

## Overview

本实现计划将语音文本处理系统分解为离散的编码步骤。实现顺序遵循从核心基础设施到业务逻辑，再到集成测试的渐进式方法。每个任务都引用具体的需求条款，确保完整的需求覆盖。

## Tasks

- [x] 1. 设置项目结构和核心配置
  - 创建项目目录结构（app/, tests/, data/）
  - 设置 FastAPI 应用和基础配置
  - 实现配置管理模块（从环境变量读取 API 密钥、数据路径、文件大小限制）
  - 配置日志系统（格式、级别、文件输出）
  - 添加启动时配置验证（缺失必需配置时拒绝启动）
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 2. 实现数据模型和验证
  - [x] 2.1 创建 Pydantic 数据模型
    - 实现 MoodData 模型（type, intensity 1-10, keywords）
    - 实现 InspirationData 模型（core_idea ≤20 字符, tags ≤5, category 枚举）
    - 实现 TodoData 模型（task, time, location, status 默认 "pending"）
    - 实现 ParsedData 模型（mood, inspirations, todos）
    - 实现 RecordData 模型（record_id, timestamp, input_type, original_text, parsed_data）
    - 实现 ProcessResponse 模型（record_id, timestamp, mood, inspirations, todos, error）
    - _Requirements: 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 6.4_

  - [x] 2.2 编写数据模型属性测试
    - **Property 6: 情绪数据结构验证**
    - **Validates: Requirements 4.1, 4.2, 4.3**

  - [x] 2.3 编写数据模型属性测试
    - **Property 7: 灵感数据结构验证**
    - **Validates: Requirements 5.1, 5.2, 5.3**

  - [x] 2.4 编写数据模型属性测试
    - **Property 8: 待办数据结构验证**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

- [x] 3. 实现存储服务（StorageService）
  - [x] 3.1 实现 JSON 文件存储管理器
    - 实现 save_record 方法（保存到 records.json，生成唯一 UUID）
    - 实现 append_mood 方法（追加到 moods.json）
    - 实现 append_inspirations 方法（追加到 inspirations.json）
    - 实现 append_todos 方法（追加到 todos.json）
    - 实现文件初始化逻辑（不存在时创建并初始化为空数组）
    - 实现错误处理（文件写入失败时抛出 StorageError）
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

  - [x] 3.2 编写存储服务属性测试
    - **Property 9: 数据持久化完整性**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4**

  - [x] 3.3 编写存储服务属性测试
    - **Property 10: 文件初始化**
    - **Validates: Requirements 7.5**

  - [x] 3.4 编写存储服务属性测试
    - **Property 11: 唯一 ID 生成**
    - **Validates: Requirements 7.7**

  - [x] 3.5 编写存储服务单元测试
    - 测试文件写入失败的错误处理
    - 测试并发写入的安全性
    - _Requirements: 7.6_

- [x] 4. 检查点 - 确保存储层测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [x] 5. 实现 ASR 服务（ASRService）
  - [x] 5.1 实现语音识别服务
    - 创建 ASRService 类，初始化 httpx.AsyncClient
    - 实现 transcribe 方法（调用智谱 ASR API）
    - 处理 API 响应，提取转写文本
    - 实现错误处理（API 调用失败时抛出 ASRServiceError）
    - 处理空识别结果（返回空字符串并标记）
    - 记录错误日志（包含时间戳和堆栈）
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 9.2, 9.5_

  - [x] 5.2 编写 ASR 服务单元测试
    - 测试 API 调用成功场景（使用 mock）
    - 测试 API 调用失败场景（使用 mock）
    - 测试空识别结果的边缘情况
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 6. 实现语义解析服务（SemanticParserService）
  - [x] 6.1 实现语义解析服务
    - 创建 SemanticParserService 类，初始化 httpx.AsyncClient
    - 配置 System Prompt（数据转换器提示词）
    - 实现 parse 方法（调用 GLM-4-Flash API）
    - 解析 API 返回的 JSON 结构
    - 处理缺失维度（返回 null 或空数组）
    - 实现错误处理（API 调用失败时抛出 SemanticParserError）
    - 记录错误日志（包含时间戳和堆栈）
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 9.2, 9.5_

  - [x] 6.2 编写语义解析服务属性测试
    - **Property 4: 解析结果结构完整性**
    - **Validates: Requirements 3.3**

  - [x] 6.3 编写语义解析服务属性测试
    - **Property 5: 缺失维度处理**
    - **Validates: Requirements 3.4**

  - [x] 6.4 编写语义解析服务单元测试
    - 测试 API 调用成功场景（使用 mock）
    - 测试 API 调用失败场景（使用 mock）
    - 测试 System Prompt 正确使用
    - 测试无情绪信息文本的边缘情况
    - 测试无灵感信息文本的边缘情况
    - 测试无待办信息文本的边缘情况
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 7. 检查点 - 确保服务层测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [x] 8. 实现 API 端点和请求处理
  - [x] 8.1 实现 POST /api/process 端点
    - 创建 FastAPI 路由处理器
    - 实现输入验证（音频格式、文件大小、文本编码）
    - 处理 multipart/form-data 格式（音频文件）
    - 处理 application/json 格式（文本内容）
    - 实现请求日志记录
    - _Requirements: 1.1, 1.2, 8.1, 8.2, 8.3_

  - [x] 8.2 实现业务逻辑编排
    - 如果是音频输入，调用 ASRService.transcribe
    - 调用 SemanticParserService.parse 进行语义解析
    - 生成 record_id 和 timestamp
    - 调用 StorageService 保存数据
    - 构建成功响应（HTTP 200，包含 record_id, timestamp, mood, inspirations, todos）
    - _Requirements: 7.7, 8.4, 8.6_

  - [x] 8.3 实现错误处理和响应
    - 捕获 ValidationError，返回 HTTP 400 和错误信息
    - 捕获 ASRServiceError，返回 HTTP 500 和"语音识别服务不可用"
    - 捕获 SemanticParserError，返回 HTTP 500 和"语义解析服务不可用"
    - 捕获 StorageError，返回 HTTP 500 和"数据存储失败"
    - 所有错误响应包含 error 字段和 timestamp
    - 记录所有错误到日志文件
    - _Requirements: 1.3, 8.5, 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 8.4 编写 API 端点属性测试
    - **Property 1: 音频格式验证**
    - **Validates: Requirements 1.1**

  - [x] 8.5 编写 API 端点属性测试
    - **Property 2: UTF-8 文本接受**
    - **Validates: Requirements 1.2**

  - [x] 8.6 编写 API 端点属性测试
    - **Property 3: 无效输入错误处理**
    - **Validates: Requirements 1.3, 9.1**

  - [x] 8.7 编写 API 端点属性测试
    - **Property 12: 成功响应格式**
    - **Validates: Requirements 8.4, 8.6**

  - [x] 8.8 编写 API 端点属性测试
    - **Property 13: 错误响应格式**
    - **Validates: Requirements 8.5, 9.1, 9.3**

  - [x] 8.9 编写 API 端点单元测试
    - 测试 POST /api/process 端点存在
    - 测试接受 multipart/form-data 格式
    - 测试接受 application/json 格式
    - _Requirements: 8.1, 8.2, 8.3_

- [x] 9. 实现日志安全性和错误日志
  - [x] 9.1 实现日志过滤器
    - 创建日志过滤器，屏蔽敏感信息（API 密钥、密码等）
    - 配置日志格式（包含 request_id, timestamp, level, message）
    - 确保错误日志包含完整堆栈信息
    - _Requirements: 9.5, 10.5_

  - [x] 9.2 编写日志属性测试
    - **Property 14: 错误日志记录**
    - **Validates: Requirements 9.5**

  - [-] 9.3 编写日志属性测试
    - **Property 15: 敏感信息保护**
    - **Validates: Requirements 10.5**

- [x] 10. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [x] 11. 集成测试
  - [x] 11.1 编写端到端集成测试
    - 测试完整流程：音频上传 → ASR → 语义解析 → 存储 → 响应
    - 测试完整流程：文本提交 → 语义解析 → 存储 → 响应
    - 测试错误场景的端到端处理
    - _Requirements: 所有需求_

- [x] 12. 最终检查点
  - 确保所有测试通过，代码覆盖率达到 80% 以上，如有问题请询问用户。

## Notes

- 所有任务均为必需任务，确保全面的测试覆盖
- 每个任务都引用了具体的需求条款，确保可追溯性
- 检查点任务确保增量验证
- 属性测试验证通用正确性属性（使用 hypothesis 库，最少 100 次迭代）
- 单元测试验证特定示例和边缘情况
- 所有外部 API 调用使用 mock 进行测试

