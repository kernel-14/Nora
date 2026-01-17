@echo off
echo ========================================
echo 启动后端服务
echo ========================================
echo.

REM 检查是否在正确的目录
if not exist "app\main.py" (
    echo 错误：找不到 app\main.py
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

echo 当前目录: %CD%
echo.

REM 激活虚拟环境（如果存在）
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
)

echo 启动 FastAPI 服务器...
echo 访问地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务器
echo.

REM 使用 python -m 方式启动，确保模块路径正确
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
