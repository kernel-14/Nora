# Hugging Face Spaces 部署检查清单

## 📋 部署前检查

### 1. 依赖版本确认
- [ ] `requirements_hf.txt` 中 `huggingface-hub==0.23.5`
- [ ] `requirements_hf.txt` 中 `gradio==4.44.0`
- [ ] `README_HF.md` frontmatter 中 `sdk_version: "4.44.0"`

### 2. 文件结构确认
- [ ] `app.py` 存在且正确
- [ ] `frontend/dist/` 已构建（运行 `cd frontend && npm run build`）
- [ ] `data/` 目录存在
- [ ] `generated_images/` 目录存在

### 3. 环境变量配置
在 Space Settings → Repository secrets 中配置：
- [ ] `ZHIPU_API_KEY` - 必需
- [ ] `MINIMAX_API_KEY` - 可选
- [ ] `MINIMAX_GROUP_ID` - 可选

## 🚀 部署步骤

### 方法 1: 使用 deploy_to_hf.sh (推荐)

```bash
# 1. 确保脚本可执行
chmod +x deploy_to_hf.sh

# 2. 运行部署脚本
./deploy_to_hf.sh
```

### 方法 2: 手动部署

```bash
# 1. 构建前端
cd frontend
npm install
npm run build
cd ..

# 2. 提交到 Git
git add .
git commit -m "Deploy to Hugging Face Spaces"

# 3. 推送到 Hugging Face
git push hf main
```

## 🐛 常见问题

### ImportError: cannot import name 'HfFolder'

**原因：** `gradio` 和 `huggingface_hub` 版本不兼容

**解决方法：**
1. 确认 `requirements_hf.txt` 版本正确
2. 在 Space Settings 中点击 "Factory reboot"
3. 查看 Container logs 确认安装的版本

### 前端 404 错误

**原因：** 前端未构建或未正确挂载

**解决方法：**
1. 本地运行 `cd frontend && npm run build`
2. 确认 `frontend/dist/` 目录存在且有内容
3. 提交并推送 `frontend/dist/` 到仓库

### API 调用失败

**原因：** 环境变量未配置

**解决方法：**
1. 在 Space Settings → Repository secrets 添加 `ZHIPU_API_KEY`
2. 重启 Space
3. 查看 Logs 确认 API 密钥已加载

## 📊 部署后验证

### 1. 健康检查
访问 `https://your-space.hf.space/health` 应返回：
```json
{
  "status": "healthy",
  "timestamp": "..."
}
```

### 2. API 文档
访问 `https://your-space.hf.space/docs` 查看 API 文档

### 3. 前端访问
访问 `https://your-space.hf.space/` 应显示应用界面

### 4. 功能测试
- [ ] 首页输入框可以输入文字
- [ ] 点击麦克风可以录音（需要浏览器权限）
- [ ] 点击 AI 形象显示对话框
- [ ] 底部导航可以切换页面

## 🔄 更新部署

### 代码更新
```bash
git add .
git commit -m "Update: description"
git push hf main
```

### 强制重建
如果遇到缓存问题：
1. 进入 Space Settings
2. 点击 "Factory reboot"
3. 等待重新构建完成

## 📝 版本兼容性

### 已测试的稳定组合

| gradio | huggingface-hub | Python | 状态 |
|--------|----------------|--------|------|
| 4.44.0 | 0.23.5 | 3.11 | ✅ 推荐 |
| 4.36.1 | 0.23.0 | 3.11 | ✅ 可用 |
| 5.x | latest | 3.11 | ❌ 不兼容 |

### 不兼容的组合

- `gradio==4.x` + `huggingface-hub>=0.24.0` → HfFolder 错误
- `gradio==5.x` + `huggingface-hub<0.24.0` → 版本冲突

## 🔗 相关资源

- [Hugging Face Spaces 文档](https://huggingface.co/docs/hub/spaces)
- [Gradio 文档](https://www.gradio.app/docs)
- [项目 README](./README.md)
