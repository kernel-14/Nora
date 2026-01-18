@echo off
echo ========================================
echo 启动本地开发服务器
echo ========================================
echo.

echo [1/2] 检查前端构建...
if not exist "frontend\dist\index.html" (
    echo 警告: 前端未构建，正在构建...
    cd frontend
    call npm run build
    if errorlevel 1 (
        echo 错误: 前端构建失败
        pause
        exit /b 1
    )
    cd ..
)
echo ✓ 前端构建检查通过

echo.
echo [2/2] 启动后端服务器...
python start_local.py

pause
