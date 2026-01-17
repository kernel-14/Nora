---

# 产品概述

一款通过 **iOS 原生 (SwiftUI)** 构建，结合 **BLE 蓝牙硬件** 震动提醒与 **AI 语义解析** 的治愈系记录助手。用户通过 APP 或配套硬件录音，系统自动将内容拆解为灵感、心情与待办，并通过 RAG 技术实现历史记忆的回溯。

# 核心交互逻辑

## 硬件交互：蓝牙协议

由于使用 iOS 原生开发，手机充当“网关”角色，负责硬件与云端的中转。

- **连接流程 (Local Only)**：
    - **无需 API 接口**。iOS APP 使用 `CBCentralManager` 扫描硬件 UUID。
    - 硬件作为外设 (Peripheral) 被手机连接。
- **指令交互**：
    - **录音阶段**：硬件按下录音键，通过蓝牙特征值 (Characteristic) 将音频数据包流式传输或发送结束信号至 iOS。
    - **震动反馈**：
        - **轻微短振（心跳感）**：iOS 检测到录音启动，向蓝牙写入 `0x01` 指令。
        - **急促振动（提醒感）**：iOS 的待办逻辑触发，向蓝牙写入 `0x02` 指令。

## AI：调用智谱原生api

- **语音转写**：iOS 使用 `URLSession` 调用智谱 **ASR API** 上传音频，实时获取转写文字。
- **语义理解**：iOS 调用 **GLM-4-Flash API**，通过 Prompt 约束 AI 返回标准 JSON（包含情绪、灵感、待办）。
- **形象定制**：登录时调用 **CogView API** 生成固定形象，图片下载后由 iOS 进行本地持久化存储。

# **技术架构 (iOS Native)**

## **前端：SwiftUI**

- **状态管理**：使用 `@Observable` (iOS 17+) 实时同步 AI 解析出的心情颜色和形象气泡。
- **持久化**：使用 **SwiftData** 存储本地 JSON 结构的记录（`records`, `moods`, `todos`, `inspirations`）。
- **安全性**：智谱 API Key 存储在 **Keychain** 中，避免硬编码。

## **AI 引擎 (智谱 API 集成)**

| **模块** | **API 模型** | **职责** |
| --- | --- | --- |
| **ASR** | 智谱语音识别 | 硬件原始音频转文字 |
| **NLP** | GLM-4-Flash | 解析 JSON 结构、RAG 历史回溯对话 |
| **图像** | CogView-3 | 登录时一次性生成固定猫咪形象 |

# AI形象生成

## 设置

- **初始化生成**：用户注册/首次登录时，系统引导用户输入关键词（或默认随机），调用 **GLM-Image (CogView)** 生成 1-3 张插画。
- **持久化存储**：生成的图片 URL 存储在用户配置中，不再随每次录音改变。
- **按需修改**：在“设置”提供修改接口，用户可以消耗积分或次数重新生成。

## 生成逻辑

为了保证品牌统一性，系统预设为”**治愈系插画猫咪**”，通过映射逻辑处理用户输入。

- **提示词生成逻辑 (Prompt Engineering)**

| **用户输入维度** | **映射逻辑 (Internal Tags)** | **示例** |
| --- | --- | --- |
| **颜色** | 主色调 & 环境色 | 温暖粉 -> `soft pastel pink fur, rose-colored aesthetic` |
| **性格** | 构图 & 眼神光 | 活泼 -> `big curious eyes, dynamic paw gesture, energetic aura` |
| **形象** | 配饰 & 特征 | 戴眼镜 -> `wearing tiny round glasses, scholarly look` |

【陪伴式朋友】【温柔照顾型长辈】【引导型 老师】

**系统底座提示词 (System Base Prompt):**

> "A masterpiece cute stylized cat illustration, [Color] theme, [Personality] facial expression and posture, [Description]. Japanese watercolor style, clean minimalist background, high quality, soft studio lighting, 4k."
> 

## 技术架构

### 前端：iOS Native (SwiftUI)

- **UI 渲染**：利用 `SwiftUI` 实现毛玻璃效果与治愈系猫咪插画的流畅加载。
- **状态管理**：使用 `Combine` 或 `Observation` 框架同步心情颜色变化。
- **硬件接口**：`CoreBluetooth`。

### 后端：FastAPI (Python)

- **API 核心**：处理 ASR、NLP、RAG 和 Image Generation。
- **存储**：本地 JSON 文件系统（`records.json`, `moods.json`, `todos.json`, `inspirations.json`）。

### AI 引擎 (智谱全家桶)

- **ASR**：语音转文字。
- **GLM-4-Flash**：语义解析与 RAG 问答。
- **GLM-Image (CogView)**：基于情绪映射生成的静态形象。

# 核心功能模块

### 首页 - 录音与实时处理

- **功能描述：**
    - 支持语音录音（5-30 秒）或文字直接输入。
    - **静态形象展示**：页面中心展示常驻形象。
    - 实时处理：完成录音后自动触发后端 ASR 与 NLP 流程。
    - **结果速览**：展示最近一次分析的**原文及摘要**（提取出的情绪、灵感标签或待办任务）。
- **数据存储：** * 音频文件：`data/audio/{timestamp}.wav`
    - 完整记录索引：`data/records.json`（包含关联的 JSON ID 和音频路径）。

### 灵感看板页面

- **功能描述：**
    - **瀑布流展示**：以卡片形式展示所有灵感。
    - **核心要素**：显示 AI 总结的核心观点、自动生成的标签、所属分类（工作/生活/学习/创意）。
    - **筛选排序**：支持按分类筛选及时间顺序/倒序排列。
- **数据结构：** `inspirations.json` 存储核心观点、关键字及原文引用。

### 心情日记页面

- **功能描述：**
    - **情绪可视化**：展示情绪分布柱状图（如：本周 60% 平静，20% 喜悦）。
    - **记录列表**：显示每条记录的情绪类型、强度（1-10）及当时的心情关键词。
    - **筛选**：可单独查看“喜”或“哀”等特定情绪的历史。
- **数据结构：** `moods.json` 记录 `type`, `intensity`, `keywords` 等字段。

### 待办清单页面

- **功能描述：**
    - **任务管理**：从输入中自动提取出的任务（包含时间、地点、内容）。
    - **状态切换**：支持手动勾选“已完成”。
    - **统计**：显示待办/已完成的数量对比。
- **数据结构：** `todos.json` 包含任务描述、时间实体及完成状态。

### AI 对话页面

- **功能描述：**
    - **智能检索**：用户询问“我上周关于论文有什么灵感？”时，系统通过 RAG 技术检索 `records.json` 并回答。
    - **快捷指令**：提供“总结今日心情”、“还有哪些待办”等快捷按钮。
- **技术实现：** 基于 **GLM-4-Flash** 进行上下文理解与 RAG 检索。

---

# 业务流程与数据流

iOS 端在请求 GLM-4 时，使用以下 System Prompt 确保数据可被解析：

> "你是一个数据转换器。请将文本解析为 JSON 格式。维度包括：1.情绪(type,intensity); 2.灵感(core_idea,tags); 3.待办(task,time,location)。必须严格遵循 JSON 格式返回。"
> 

### NLP 语义解析策略

| **提取维度** | **逻辑** | **去向** |
| --- | --- | --- |
| **情绪** | 识别情感极性与 1-10 的强度值 | `moods.json` |
| **灵感** | 提炼 20 字以内的核心观点 + 3个标签 | `inspirations.json` |
| **待办** | 识别时间词（如“明晚”）、地点与动词短语 | `todos.json` |

# 技术栈总结

- **开发语言**：Swift 6.0 / SwiftUI
- **核心框架**：CoreBluetooth (硬件), SwiftData (存储), CoreHaptics (震动)
- **AI 接口**：智谱 API (HTTP/HTTPS 请求)
- **数据存储**：iOS Local SandBox (音频文件 + 结构化数据)