# API 配置说明

## 自动检测 API 地址

前端应用会自动检测运行环境并配置正确的 API 地址。

### 支持的环境

#### 1. 生产环境（自动检测）

**Hugging Face Spaces:**
- 域名包含：`hf.space`, `huggingface.co`, `gradio.live`
- API 地址：使用相同的协议和域名
- 示例：`https://huggingface.co/spaces/kernel14/Nora`
  - 前端：`https://huggingface.co/spaces/kernel14/Nora`
  - API：`https://huggingface.co/spaces/kernel14/Nora/api/...`

**ModelScope:**
- 域名包含：`modelscope.cn`
- API 地址：使用相同的协议和域名
- 示例：`https://modelscope.cn/studios/xxx/yyy`
  - 前端：`https://modelscope.cn/studios/xxx/yyy`
  - API：`https://modelscope.cn/studios/xxx/yyy/api/...`

#### 2. 局域网访问

**通过 IP 地址访问：**
- 前端：`http://192.168.1.100:5173`
- API：`http://192.168.1.100:8000`

**通过主机名访问：**
- 前端：`http://mycomputer.local:5173`
- API：`http://mycomputer.local:8000`

#### 3. 本地开发

**默认配置：**
- 前端：`http://localhost:5173`
- API：`http://localhost:8000`

### 环境变量配置（可选）

如果需要手动指定 API 地址，可以在前端项目中创建 `.env.local` 文件：

```env
VITE_API_URL=https://your-custom-api-url.com
```

### 检测逻辑

```typescript
const getApiBaseUrl = () => {
  // 1. 优先使用环境变量
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // 2. 检测生产环境（Hugging Face, ModelScope）
  if (hostname.includes('hf.space') || 
      hostname.includes('huggingface.co') || 
      hostname.includes('modelscope.cn')) {
    return `${protocol}//${hostname}`;
  }
  
  // 3. 检测局域网访问
  if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return `${protocol}//${hostname}:8000`;
  }
  
  // 4. 默认本地开发
  return 'http://localhost:8000';
};
```

### 调试

打开浏览器控制台，查看 API 地址：

```
🔗 API Base URL: https://huggingface.co/spaces/kernel14/Nora
```

### 常见问题

**Q: 为什么其他设备无法访问？**

A: 确保：
1. 后端服务器绑定到 `0.0.0.0` 而不是 `127.0.0.1`
2. 防火墙允许端口 8000
3. 使用正确的 IP 地址访问

**Q: Hugging Face 上 API 调用失败？**

A: 检查：
1. 浏览器控制台的 API 地址是否正确
2. 是否配置了必需的环境变量（`ZHIPU_API_KEY`）
3. 查看 Space 的日志是否有错误

**Q: 如何测试 API 连接？**

A: 访问以下地址：
- 健康检查：`/health`
- API 文档：`/docs`
- 测试页面：`/test_api.html`

### 部署检查清单

- [ ] 前端已重新构建（`npm run build`）
- [ ] `frontend/dist/` 已提交到 Git
- [ ] 环境变量已配置（Hugging Face Secrets / ModelScope 环境变量）
- [ ] Space 已重启
- [ ] 浏览器控制台显示正确的 API 地址
- [ ] 测试 API 调用是否成功
