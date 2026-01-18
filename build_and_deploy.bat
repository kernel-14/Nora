@echo off
echo ========================================
echo 构建并部署到 Hugging Face Spaces
echo ========================================
echo.

echo [1/4] 构建前端...
cd frontend
call npm install
if errorlevel 1 (
    echo 错误: npm install 失败
    pause
    exit /b 1
)

call npm run build
if errorlevel 1 (
    echo 错误: npm run build 失败
    pause
    exit /b 1
)
cd ..

echo.
echo [2/4] 检查构建产物...
if not exist "frontend\dist\index.html" (
    echo 错误: 构建产物不存在
    pause
    exit /b 1
)
echo ✓ 构建产物检查通过

echo.
echo [3/4] 提交到 Git...
git add .
git commit -m "Build: Update frontend dist for deployment"
if errorlevel 1 (
    echo 提示: 没有新的更改需要提交
)

echo.
echo [4/4] 推送到 Hugging Face...
git push hf main
if errorlevel 1 (
    echo 错误: 推送失败
    echo 请检查 Hugging Face 远程仓库配置
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ 部署完成！
echo ========================================
echo.
echo 访问你的 Hugging Face Space 查看应用
pause
