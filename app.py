"""
Hugging Face Spaces 入口文件
使用 Gradio 挂载 FastAPI 应用
"""

import gradio as gr
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置环境变量
os.environ.setdefault("DATA_DIR", "data")
os.environ.setdefault("LOG_LEVEL", "INFO")

# 确保数据目录存在
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

generated_images_dir = Path("generated_images")
generated_images_dir.mkdir(exist_ok=True)

# 导入 FastAPI 应用
from app.main import app as fastapi_app
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 挂载前端静态文件
frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.exists():
    # 先挂载静态资源（CSS, JS）
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        fastapi_app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        print(f"✅ 前端资源文件已挂载: {assets_dir}")
    
    # 添加根路径和所有未匹配路径返回 index.html（SPA 路由支持）
    @fastapi_app.get("/app")
    @fastapi_app.get("/app/{full_path:path}")
    async def serve_frontend(full_path: str = ""):
        """服务前端应用"""
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"error": "Frontend not found"}
    
    print(f"✅ 前端应用已挂载到 /app 路径: {frontend_dist}")
else:
    print(f"⚠️ 前端构建目录不存在: {frontend_dist}")
    print("请先构建前端: cd frontend && npm install && npm run build")

# 创建 Gradio 界面（用于 Hugging Face Spaces 的展示）
with gr.Blocks(
    title="治愈系记录助手 - SoulMate AI Companion",
    theme=gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="pink",
    ),
) as demo:
    
    gr.Markdown("""
    # 🌟 治愈系记录助手 - SoulMate AI Companion
    
    一个温暖、治愈的 AI 陪伴应用，帮助你记录心情、捕捉灵感、管理待办。
    
    ### ✨ 核心特性
    - 🎤 **语音/文字快速记录** - 自动分类保存
    - 🤖 **AI 语义解析** - 智能提取情绪、灵感和待办
    - 💬 **AI 对话陪伴（RAG）** - 基于历史记录的个性化对话
    - 🖼️ **AI 形象定制** - 生成专属治愈系角色（720 种组合）
    - 🫧 **物理引擎心情池** - 基于 Matter.js 的动态气泡可视化
    
    ---
    
    ### 🚀 开始使用
    
    **🎯 前端应用地址：** [点击这里访问完整应用 →](/app)
    
    **📚 API 文档：** [FastAPI Swagger Docs →](/docs)
    
    ---
    
    gr.Markdown("""
    ### 📖 使用说明
    
    1. **首页快速记录**
       - 点击麦克风录音或在输入框输入文字
       - AI 自动分析并分类保存
    
    2. **查看分类数据**
       - 点击顶部"心情"、"灵感"、"待办"图标
       - 查看不同类型的记录
    
    3. **与 AI 对话**
       - 点击 AI 形象显示问候对话框
       - 点击对话框中的聊天图标进入完整对话
       - AI 基于你的历史记录提供个性化回复
    
    4. **定制 AI 形象**
       - 点击右下角 ✨ 按钮
       - 选择颜色、性格、外观、角色
       - 生成专属形象（需要 MiniMax API）
    
    5. **心情气泡池**
       - 点击顶部"心情"图标
       - 左右滑动查看不同日期的心情卡片
       - 点击卡片展开查看当天的气泡池
       - 可以拖拽气泡，感受物理引擎效果
    
    ---
    
    ### ⚙️ 配置说明
    
    需要在 Hugging Face Spaces 的 **Settings → Repository secrets** 中配置：
    
    **必需：**
    - `ZHIPU_API_KEY` - 智谱 AI API 密钥
      - 获取地址：https://open.bigmodel.cn/
      - 用途：语音识别、语义解析、AI 对话
    
    **可选：**
    - `MINIMAX_API_KEY` - MiniMax API 密钥
    - `MINIMAX_GROUP_ID` - MiniMax Group ID
      - 获取地址：https://platform.minimaxi.com/
      - 用途：AI 形象生成
    
    ---
    
    ### 🔗 相关链接
    - [GitHub 仓库](https://github.com/your-username/your-repo)
    - [详细文档](https://github.com/your-username/your-repo/blob/main/README.md)
    - [智谱 AI](https://open.bigmodel.cn/)
    - [MiniMax](https://platform.minimaxi.com/)
    
    ---
    
    ### 📊 API 端点
    
    - `POST /api/process` - 处理文本/语音输入
    - `POST /api/chat` - 与 AI 对话（RAG）
    - `GET /api/records` - 获取所有记录
    - `GET /api/moods` - 获取情绪数据
    - `GET /api/inspirations` - 获取灵感
    - `GET /api/todos` - 获取待办事项
    - `POST /api/character/generate` - 生成角色形象
    - `GET /health` - 健康检查
    - `GET /docs` - API 文档
    """)

# 挂载 FastAPI 到 Gradio
app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

# 如果直接运行此文件
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
