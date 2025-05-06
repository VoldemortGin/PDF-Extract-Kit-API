FROM paddlepaddle/paddle:2.5.0-gpu-cuda11.7-cudnn8.4-trt8.4

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    poppler-utils \
    wget \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装uv
RUN pip install --no-cache-dir uv

# 创建必要的目录
RUN mkdir -p data/uploads data/outputs data/logs data/static models

# 仅复制依赖文件
COPY requirements.txt .

# 使用uv安装Python依赖
RUN uv pip install --system -r requirements.txt

# 复制模型下载脚本和配置相关文件
COPY .project-root .
COPY src/download_models.py ./src/download_models.py
COPY configs/ ./configs/

# 下载模型
RUN python src/download_models.py

# 设置环境变量
ENV PYTHONPATH=/app
ENV IS_PROD=True
# 设置环境变量以使用GPU
ENV CUDA_VISIBLE_DEVICES=0

# 复制环境文件 (.env.prod -> .env)
COPY .env.prod ./.env

# 暴露端口
EXPOSE 8000

# 最后才复制其余源代码文件（这样修改代码时可以利用缓存）
COPY main.py .
COPY pdf_extract_kit/ ./pdf_extract_kit/
COPY src/ ./src/

# 启动应用
CMD ["python", "main.py"]
