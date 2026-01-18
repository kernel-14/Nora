"""
启动脚本 - 不使用 Gradio，直接运行 FastAPI
"""

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
from app.main import app
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Request

# 检查前端构建目录
frontend_dist = Path(__file__).parent / "frontend" / "dist"
frontend_exists = frontend_dist.exists()

if frontend_exists:
    # 挂载静态资源（CSS, JS）
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        print(f"✅ 前端资源文件已挂载: {assets_dir}")
    
    print(f"✅ 前端应用已挂载: {frontend_dist}")
else:
    print(f"⚠️ 前端构建目录不存在: {frontend_dist}")

# 重写根路径路由以服务前端
@app.get("/", include_in_schema=False)
async def serve_root():
    """服务前端应用首页"""
    if frontend_exists:
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
    return {
        "service": "SoulMate AI Companion",
        "status": "running",
        "version": "1.0.0",
        "message": "Frontend not available. Please visit /docs for API documentation."
    }

# 添加 catch-all 路由用于 SPA（必须放在最后）
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str, request: Request):
    """服务前端应用（SPA 路由支持）"""
    # 如果是 API 路径，跳过（让 FastAPI 处理 404）
    if full_path.startswith("api/") or full_path == "docs" or full_path == "openapi.json" or full_path == "health":
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    
    # 返回前端 index.html
    if frontend_exists:
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
    
    return {"error": "Frontend not found"}

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("🌟 治愈系记录助手 - SoulMate AI Companion")
    print("=" * 50)
    print(f"📍 前端应用: http://0.0.0.0:7860/")
    print(f"📚 API 文档: http://0.0.0.0:7860/docs")
    print(f"🔍 健康检查: http://0.0.0.0:7860/health")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
        log_level="info"
    )

