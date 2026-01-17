@echo off
chcp 65001 >nul
echo 🚀 开始部署到 Hugging Face Spaces...
echo.

REM 检查是否已登录
huggingface-cli whoami >nul 2>&1
if errorlevel 1 (
    echo ❌ 请先登录 Hugging Face CLI
    echo 运行: huggingface-cli login
    pause
    exit /b 1
)

REM 获取用户名
for /f "tokens=2" %%i in ('huggingface-cli whoami ^| findstr "username:"') do set USERNAME=%%i
echo ✅ 已登录为: %USERNAME%
echo.

REM 询问 Space 名称
set /p SPACE_NAME="请输入 Space 名称 (默认: soulmate-ai-companion): "
if "%SPACE_NAME%"=="" set SPACE_NAME=soulmate-ai-companion

echo.
echo 📦 准备文件...

REM 构建前端
echo 🔨 构建前端...
cd frontend
call npm install
call npm run build
cd ..

if not exist "frontend\dist" (
    echo ❌ 前端构建失败
    pause
    exit /b 1
)

echo ✅ 前端构建完成
echo.

REM 创建临时目录
set TEMP_DIR=temp_hf_deploy
if exist %TEMP_DIR% rmdir /s /q %TEMP_DIR%
mkdir %TEMP_DIR%

REM 复制文件
echo 📋 复制文件...
copy app.py %TEMP_DIR%\
copy requirements_hf.txt %TEMP_DIR%\requirements.txt
copy README_HF.md %TEMP_DIR%\README.md
copy .gitattributes %TEMP_DIR%\
xcopy /E /I /Y app %TEMP_DIR%\app
xcopy /E /I /Y frontend\dist %TEMP_DIR%\frontend
mkdir %TEMP_DIR%\data
mkdir %TEMP_DIR%\generated_images

REM 创建或克隆 Space
echo 🌐 准备 Space...
set SPACE_URL=https://huggingface.co/spaces/%USERNAME%/%SPACE_NAME%

huggingface-cli repo info spaces/%USERNAME%/%SPACE_NAME% >nul 2>&1
if errorlevel 1 (
    echo 🆕 创建新 Space...
    huggingface-cli repo create %SPACE_NAME% --type space --space_sdk gradio
) else (
    echo ✅ Space 已存在
)

cd %TEMP_DIR%
git clone %SPACE_URL% .

REM 复制文件到仓库
echo 📤 准备上传...
copy ..\app.py .
copy ..\requirements_hf.txt requirements.txt
copy ..\README_HF.md README.md
copy ..\.gitattributes .
xcopy /E /I /Y ..\app app
xcopy /E /I /Y ..\frontend\dist frontend
if not exist data mkdir data
if not exist generated_images mkdir generated_images

REM 提交并推送
echo 🚀 上传到 Hugging Face...
git add .
git commit -m "Deploy to Hugging Face Spaces"
git push

cd ..
rmdir /s /q %TEMP_DIR%

echo.
echo ✅ 部署完成！
echo.
echo 📍 Space URL: %SPACE_URL%
echo.
echo ⚙️  下一步：
echo 1. 访问 %SPACE_URL%
echo 2. 点击 Settings → Repository secrets
echo 3. 添加环境变量：
echo    - ZHIPU_API_KEY (必需)
echo    - MINIMAX_API_KEY (可选)
echo    - MINIMAX_GROUP_ID (可选)
echo.
echo 🎉 完成后即可使用！
echo.
pause
