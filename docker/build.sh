#!/bin/bash

# 设置变量
IMAGE_NAME="pdf-extract-kit-api"
IMAGE_TAG="latest"

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 构建Docker镜像
echo "正在构建 $IMAGE_NAME:$IMAGE_TAG 镜像..."
docker build -t $IMAGE_NAME:$IMAGE_TAG -f docker/Dockerfile .

# 检查构建结果
if [ $? -eq 0 ]; then
  echo "镜像构建成功: $IMAGE_NAME:$IMAGE_TAG"
  echo "你可以使用以下命令运行容器:"
  echo "docker run -p 8000:8000 -v \$(pwd)/data:/app/data $IMAGE_NAME:$IMAGE_TAG"
else
  echo "镜像构建失败"
  exit 1
fi 