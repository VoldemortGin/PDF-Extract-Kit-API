# PDF Extract Kit API Docker 构建和运行命令

# 变量定义
IMAGE_NAME = pdf-extract-kit-api
# 基础镜像标签
BASE_TAG = latest
# 日期格式：YYYYMMDD
DATE_TAG = $(shell date +%Y%m%d)
# 计数文件路径
COUNT_FILE = .build_count
# 如果计数文件不存在，则创建并初始化为0
$(shell if [ ! -f $(COUNT_FILE) ]; then echo "0" > $(COUNT_FILE); fi)
# 读取当前计数
CURRENT_COUNT = $(shell cat $(COUNT_FILE))
# 检查当前日期是否已经改变
CURRENT_DATE_IN_FILE = $(shell if [ -f .build_date ]; then cat .build_date; else echo ""; fi)
# 如果日期已更改，重置计数
$(shell if [ "$(DATE_TAG)" != "$(CURRENT_DATE_IN_FILE)" ]; then echo "0" > $(COUNT_FILE); echo "$(DATE_TAG)" > .build_date; fi)
# 增加计数（新计数 = 当前计数 + 1）
NEW_COUNT = $(shell echo $$(($(CURRENT_COUNT) + 1)))
# 生成格式化的计数（例如：01、02、03...）
BUILD_COUNT = $(shell printf "%02d" $(NEW_COUNT))
# 生成最终标签格式：YYYYMMDD-NN
IMAGE_TAG = $(DATE_TAG)-$(BUILD_COUNT)

CONTAINER_NAME = pdf-extract-kit-container
HOST_PORT = 8000
CONTAINER_PORT = 8000

# Docker数据卷映射
DATA_VOLUME = $(shell pwd)/data:/app/data

# 默认目标
.PHONY: help
help:
	@echo "使用方法:"
	@echo "  make build        - 构建Docker镜像（自动生成标签格式：YYYYMMDD-NN）"
	@echo "  make run          - 运行Docker容器"
	@echo "  make run-d        - 以后台模式运行Docker容器"
	@echo "  make stop         - 停止Docker容器"
	@echo "  make rm           - 移除Docker容器"
	@echo "  make logs         - 查看Docker容器日志"
	@echo "  make sh           - 进入Docker容器Shell"
	@echo "  make clean        - 移除Docker镜像和容器"
	@echo "  make current-tag  - 显示当前的镜像标签"

# 构建Docker镜像
.PHONY: build
build:
	@echo "构建 $(IMAGE_NAME):$(IMAGE_TAG) 镜像..."
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) -t $(IMAGE_NAME):latest -f docker/Dockerfile .
	@# 更新计数
	@echo $(NEW_COUNT) > $(COUNT_FILE)
	@echo "镜像已构建并标记为: $(IMAGE_NAME):$(IMAGE_TAG)"

# 显示当前的镜像标签
.PHONY: current-tag
current-tag:
	@echo "当前镜像标签: $(IMAGE_NAME):$(IMAGE_TAG)"

# 运行Docker容器
.PHONY: run
run:
	@echo "运行 $(CONTAINER_NAME) 容器..."
	docker run --rm --name $(CONTAINER_NAME) \
		-p $(HOST_PORT):$(CONTAINER_PORT) \
		-v $(DATA_VOLUME) \
		--gpus all \
		$(IMAGE_NAME):$(IMAGE_TAG)

# 以后台模式运行Docker容器
.PHONY: run-d
run-d:
	@echo "以后台模式运行 $(CONTAINER_NAME) 容器..."
	docker run -d --name $(CONTAINER_NAME) \
		-p $(HOST_PORT):$(CONTAINER_PORT) \
		-v $(DATA_VOLUME) \
		--gpus all \
		$(IMAGE_NAME):$(IMAGE_TAG)

# 停止Docker容器
.PHONY: stop
stop:
	@echo "停止 $(CONTAINER_NAME) 容器..."
	docker stop $(CONTAINER_NAME)

# 移除Docker容器
.PHONY: rm
rm:
	@echo "移除 $(CONTAINER_NAME) 容器..."
	docker rm $(CONTAINER_NAME)

# 查看Docker容器日志
.PHONY: logs
logs:
	@echo "查看 $(CONTAINER_NAME) 容器日志..."
	docker logs -f $(CONTAINER_NAME)

# 进入Docker容器Shell
.PHONY: sh
sh:
	@echo "进入 $(CONTAINER_NAME) 容器Shell..."
	docker exec -it $(CONTAINER_NAME) /bin/bash

# 清理Docker镜像和容器
.PHONY: clean
clean: stop rm
	@echo "移除 $(IMAGE_NAME):$(IMAGE_TAG) 镜像..."
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG)
