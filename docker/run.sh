#!/bin/bash

# 设置变量
IMAGE_NAME="pdf-extract-kit-api"
IMAGE_TAG="latest"
CONTAINER_NAME="pdf-extract-kit-api"
HOST_PORT=8000
CONTAINER_PORT=8000

# 检查是否已有同名容器正在运行
RUNNING_CONTAINER=$(docker ps -q -f name=$CONTAINER_NAME)
if [ ! -z "$RUNNING_CONTAINER" ]; then
  echo "容器 $CONTAINER_NAME 已经在运行中"
  echo "你可以使用以下命令停止它:"
  echo "docker stop $CONTAINER_NAME"
  exit 1
fi

# 检查是否存在同名但已停止的容器
STOPPED_CONTAINER=$(docker ps -aq -f name=$CONTAINER_NAME)
if [ ! -z "$STOPPED_CONTAINER" ]; then
  echo "正在移除已停止的容器 $CONTAINER_NAME..."
  docker rm $CONTAINER_NAME
fi

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 确保数据目录存在
mkdir -p data/uploads data/outputs data/logs data/static

# 运行容器
echo "正在启动 $CONTAINER_NAME 容器..."
docker run -d \
  --name $CONTAINER_NAME \
  -p $HOST_PORT:$CONTAINER_PORT \
  -v "$(pwd)/data:/app/data" \
  $IMAGE_NAME:$IMAGE_TAG

# 检查启动结果
if [ $? -eq 0 ]; then
  echo "容器 $CONTAINER_NAME 已成功启动"
  echo "API服务现在可以通过 http://localhost:$HOST_PORT 访问"
  echo "Swagger文档: http://localhost:$HOST_PORT/docs"
  echo "你可以使用以下命令查看日志:"
  echo "docker logs -f $CONTAINER_NAME"
else
  echo "容器启动失败"
  exit 1
fi 