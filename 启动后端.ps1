# PowerShell 启动脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动后端服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否在正确的目录
if (-not (Test-Path "app\main.py")) {
    Write-Host "错误：找不到 app\main.py" -ForegroundColor Red
    Write-Host "请确保在项目根目录运行此脚本" -ForegroundColor Red
    Read-Host "按 Enter 键退出"
    exit 1
}

Write-Host "当前目录: $PWD" -ForegroundColor Green
Write-Host ""

# 激活虚拟环境（如果存在）
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "激活虚拟环境..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

Write-Host "启动 FastAPI 服务器..." -ForegroundColor Green
Write-Host "访问地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API 文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""

# 使用 python -m 方式启动，确保模块路径正确
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
