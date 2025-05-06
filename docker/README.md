# PDF-Extract-Kit API Docker部署指南

本文档提供了使用Docker部署PDF-Extract-Kit API的详细步骤。

## 1. 环境要求

- Docker 20.10.0或更高版本
- 至少4GB RAM (推荐8GB或更多)
- 至少20GB磁盘空间 (视模型大小可能需要更多)
- 对于GPU支持:
  - NVIDIA GPU 
  - NVIDIA驱动 >= 450.80.02
  - NVIDIA Container Toolkit (nvidia-docker2)

## 2. 构建镜像

```bash
# 给构建脚本添加执行权限
chmod +x docker/build.sh

# 运行构建脚本
./docker/build.sh
```

或者手动构建:

```bash
# 在项目根目录下执行
docker build -t pdf-extract-kit-api:latest -f docker/Dockerfile .
```

## 3. 运行容器

### 3.1 CPU版本

```bash
# 给运行脚本添加执行权限
chmod +x docker/run.sh

# 运行容器脚本
./docker/run.sh
```

或者手动运行:

```bash
# 在项目根目录下执行
docker run -d \
  --name pdf-extract-kit-api \
  -p 8000:8000 \
  -v "$(pwd)/data:/app/data" \
  pdf-extract-kit-api:latest
```

### 3.2 GPU版本

确保已安装NVIDIA Container Toolkit，可参考[NVIDIA官方文档](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)进行安装。

```bash
# 给GPU运行脚本添加执行权限
chmod +x docker/run_gpu.sh

# 运行GPU版容器脚本
./docker/run_gpu.sh
```

或者手动运行:

```bash
# 在项目根目录下执行
docker run -d \
  --name pdf-extract-kit-api-gpu \
  --gpus all \
  -p 8000:8000 \
  -v "$(pwd)/data:/app/data" \
  pdf-extract-kit-api:latest
```

## 4. 访问API

构建和运行成功后，可以通过以下地址访问API：

- API主页: http://localhost:8000
- API文档: http://localhost:8000/docs

## 5. 管理容器

```bash
# 查看容器日志
docker logs -f pdf-extract-kit-api

# 停止容器
docker stop pdf-extract-kit-api

# 启动已停止的容器
docker start pdf-extract-kit-api

# 删除容器
docker rm pdf-extract-kit-api

# 删除镜像
docker rmi pdf-extract-kit-api:latest
```

对于GPU版本，将容器名称替换为`pdf-extract-kit-api-gpu`即可。

## 6. 数据持久化

所有数据存储在`data/`目录中，该目录已通过卷(volume)映射到容器内的`/app/data`：

- `data/uploads/`: 上传的PDF文件
- `data/outputs/`: 处理结果
- `data/logs/`: 日志文件
- `data/static/`: 静态资源

## 7. 配置说明

可以通过环境变量配置容器运行参数，例如：

```bash
docker run -d \
  --name pdf-extract-kit-api \
  -p 8000:8000 \
  -e IS_PROD=True \
  -e CUDA_VISIBLE_DEVICES=0 \
  -v "$(pwd)/data:/app/data" \
  pdf-extract-kit-api:latest
```

## 8. 使用uv管理Python依赖

本项目在Docker中使用uv来管理Python依赖，这提供了更快的安装速度和更好的依赖解析。如果需要在容器内安装额外的Python包，可以使用：

```bash
docker exec -it pdf-extract-kit-api bash
uv pip install --system package_name
```

## 9. 注意事项

- 首次运行时，系统会自动下载模型，这可能需要一些时间
- 请确保容器有足够的资源运行深度学习模型
- 使用GPU版本可以大幅提升处理速度，特别是对于复杂的布局检测和OCR任务
- 使用GPU版本时，需要确保主机上的NVIDIA驱动版本与容器内CUDA版本兼容

## 生产环境部署

### 使用 prod.Dockerfile

项目提供了专门用于生产环境的 `prod.Dockerfile`，与开发环境的主要区别在于：

1. 设置 `IS_PROD=True` 环境变量
2. 使用 `.env.prod` 文件作为环境配置
3. 禁用热重载功能

### 环境变量配置

在生产环境中，请创建 `.env.prod` 文件，包含生产环境专用的配置：

```
# 生产环境配置

# 应用设置
IS_PROD=True
DEBUG=False

# API配置
API_HOST=0.0.0.0
API_PORT=8000

# 日志设置
LOG_LEVEL=INFO
LOG_FILE=data/logs/app.log

# 资源设置
MAX_WORKERS=4

# GPU配置
CUDA_VISIBLE_DEVICES=0

# 模型下载配置（如需使用HuggingFace私有模型）
# HF_TOKEN=your_huggingface_token

# 安全设置
# API_KEY=your_api_key_for_production
```

### 构建和运行生产环境容器

```bash
# 构建生产环境镜像
docker build -t pdf-extract-kit-api:prod -f docker/prod.Dockerfile .

# 运行生产环境容器
docker run -d --gpus all -p 8000:8000 -v $(pwd)/data:/app/data --name pdf-extract-api-prod pdf-extract-kit-api:prod
``` 