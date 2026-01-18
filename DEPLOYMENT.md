# 部署指南

## 部署到 Hugging Face Spaces

### 前置准备

1. **构建前端**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **验证构建产物**
   - 确保 `frontend/dist/` 目录存在
   - 包含 `index.html` 和 `assets/` 文件夹

### 自动部署（推荐）

**Windows:**
```bash
build_and_deploy.bat
```

**Linux/Mac:**
```bash
chmod +x build_and_deploy.sh
./build_and_deploy.sh
```

### 手动部署

1. **构建前端**
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

2. **提交更改**
   ```bash
   git add .
   git commit -m "Deploy: Update frontend build"
   ```

3. **推送到 Hugging Face**
   ```bash
   git push hf main
   ```

### 配置 Hugging Face Secrets

在 Space 的 Settings → Repository secrets 中添加：

**必需：**
- `ZHIPU_API_KEY` - 智谱 AI API 密钥
  - 获取：https://open.bigmodel.cn/

**可选：**
- `MINIMAX_API_KEY` - MiniMax API 密钥
- `MINIMAX_GROUP_ID` - MiniMax Group ID
  - 获取：https://platform.minimaxi.com/

### 访问应用

部署成功后，访问：
- **前端应用**: `https://your-space.hf.space/app`
- **Gradio 界面**: `https://your-space.hf.space/gradio`
- **API 文档**: `https://your-space.hf.space/docs`

### 文件结构

```
.
├── app.py                 # Hugging Face 入口文件
├── app/                   # FastAPI 后端
│   ├── main.py           # 主应用
│   └── ...
├── frontend/
│   ├── dist/             # 构建产物（需要提交）
│   │   ├── index.html
│   │   └── assets/
│   └── ...
├── requirements_hf.txt   # Python 依赖
└── README_HF.md          # Hugging Face 说明
```

### 故障排查

**问题：前端 404**
- 检查 `frontend/dist/` 是否存在
- 确认已运行 `npm run build`
- 查看 Space 日志确认文件已上传

**问题：API 调用失败**
- 检查 Secrets 是否正确配置
- 查看 Space 日志中的错误信息
- 确认 API 密钥有效

**问题：静态资源加载失败**
- 检查 `frontend/dist/assets/` 是否存在
- 确认 CSS 和 JS 文件已生成
- 查看浏览器控制台的网络请求

### 本地测试

在部署前本地测试：

```bash
# 构建前端
cd frontend && npm run build && cd ..

# 运行应用
python app.py
```

访问 `http://localhost:7860/app` 测试前端应用。

### 更新部署

每次修改前端代码后：

1. 重新构建：`cd frontend && npm run build && cd ..`
2. 提交更改：`git add . && git commit -m "Update"`
3. 推送：`git push hf main`

### 注意事项

- ✅ `frontend/dist/` 必须提交到 Git（不要在 .gitignore 中忽略）
- ✅ 每次修改前端代码都需要重新构建
- ✅ Hugging Face Spaces 会自动重启应用
- ⚠️ 首次部署可能需要 5-10 分钟
- ⚠️ 免费 Space 可能会在不活跃时休眠
