# 文档目录

本目录包含项目的详细技术文档。

## 📚 文档列表

### 核心文档

- **[功能架构图.md](功能架构图.md)** - 系统架构、数据流向、组件关系图
- **[FEATURE_SUMMARY.md](FEATURE_SUMMARY.md)** - 功能实现总结（英文）

### 故障排查

- **[后端启动问题排查.md](后端启动问题排查.md)** - 后端启动常见问题和解决方案
- **[语音录制问题排查.md](语音录制问题排查.md)** - 语音录制功能的使用和故障排查

## 🔗 相关文档

### 根目录文档

- **[README.md](../README.md)** - 项目主文档
- **[PRD.md](../PRD.md)** - 产品需求文档

### 测试文件

- **[test_home_input.py](../test_home_input.py)** - 首页输入功能测试
- **[test_audio_recording.html](../test_audio_recording.html)** - 音频录制测试页面
- **[诊断环境.py](../诊断环境.py)** - 环境诊断脚本

## 📖 快速导航

### 我想...

- **启动应用** → 查看 [README.md](../README.md) 的"快速开始"部分
- **解决启动问题** → 查看 [后端启动问题排查.md](后端启动问题排查.md)
- **了解语音录制** → 查看 [语音录制问题排查.md](语音录制问题排查.md)
- **了解系统架构** → 查看 [功能架构图.md](功能架构图.md)
- **查看功能实现** → 查看 [FEATURE_SUMMARY.md](FEATURE_SUMMARY.md)

## 🛠️ 工具和脚本

### 诊断工具

```bash
# 环境诊断
python 诊断环境.py

# 功能测试
python test_home_input.py
```

### 启动脚本

```bash
# Windows CMD
启动后端.bat

# PowerShell
.\启动后端.ps1
```

### 测试页面

- 打开 `test_audio_recording.html` 测试音频录制功能

## 📝 文档维护

### 文档结构

```
项目根目录/
├── README.md              # 主文档
├── PRD.md                 # 产品需求文档
├── docs/                  # 详细文档目录
│   ├── README.md          # 本文件
│   ├── 功能架构图.md      # 架构文档
│   ├── 后端启动问题排查.md # 启动问题
│   ├── 语音录制问题排查.md # 录音问题
│   └── FEATURE_SUMMARY.md # 功能总结
├── test_home_input.py     # 测试脚本
├── test_audio_recording.html # 测试页面
└── 诊断环境.py            # 诊断脚本
```

### 更新文档

如需更新文档，请：
1. 修改对应的 Markdown 文件
2. 确保链接正确
3. 更新本 README 的文档列表

## 🤝 贡献

欢迎改进文档！如果你发现：
- 文档有错误
- 说明不清楚
- 缺少重要信息

请提交 Issue 或 Pull Request。

---

**最后更新：** 2024-01-17
