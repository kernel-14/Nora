FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/
COPY data/ ./data/
COPY frontend/dist/ ./frontend/dist/

# 复制启动脚本
COPY start.py .

# 创建必要的目录
RUN mkdir -p generated_images logs

# 暴露端口
EXPOSE 7860

# 启动应用
CMD ["python", "start.py"]
