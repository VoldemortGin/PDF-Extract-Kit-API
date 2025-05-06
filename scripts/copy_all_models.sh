#!/bin/bash

# 脚本用于从modelscope缓存复制所有模型到项目目录
# 作者: ChatGPT
# 日期: 2025-05-02

echo "=== 开始复制所有模型 ==="

# 源目录和目标目录
SRC_DIR=~/.cache/modelscope/hub/models/opendatalab/PDF-Extract-Kit-1___0/models
DEST_DIR=./models

# 检查源目录是否存在
if [ ! -d "$SRC_DIR" ]; then
    echo "错误: 源目录不存在: $SRC_DIR"
    echo "请先运行 python scripts/download_models.py 下载模型"
    exit 1
fi

# 创建目标目录(如果不存在)
mkdir -p "$DEST_DIR"

# 复制整个目录
echo "正在复制所有模型文件..."
cp -R "$SRC_DIR"/* "$DEST_DIR"/

# 检查复制是否成功
if [ $? -eq 0 ]; then
    echo "所有模型已成功复制到 $DEST_DIR"
    echo "现在应该可以正常使用所有功能了！"
    
    # 列出主要模型文件作为确认
    echo -e "\n主要模型文件确认:"
    ls -la "$DEST_DIR"/Layout/YOLO/doclayout_yolo_ft.pt 2>/dev/null || echo "布局检测模型缺失"
    ls -la "$DEST_DIR"/MFD/YOLO/yolo_v8_ft.pt 2>/dev/null || echo "公式检测模型缺失"
else
    echo "复制过程中出现错误，请检查权限或磁盘空间"
fi

echo "=== 复制过程完成 ===" 