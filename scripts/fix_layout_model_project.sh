#!/bin/bash

# 脚本用于从modelscope缓存复制布局检测模型到项目目录
# 作者: ChatGPT
# 日期: 2023-10-17

echo "=== 开始修复布局检测模型问题 ==="

# 1. 创建目标目录
echo "正在创建目标目录..."
mkdir -p models/Layout/YOLO

# 2. 检查模型是否在modelscope缓存中
CACHE_DIR=~/.cache/modelscope/hub/models/opendatalab/PDF-Extract-Kit-1___0/models/Layout/YOLO
MODEL_FILE=doclayout_yolo_ft.pt
TARGET_DIR=models/Layout/YOLO

if [ -f "$CACHE_DIR/$MODEL_FILE" ]; then
    echo "在modelscope缓存中找到模型文件，正在复制..."
    cp "$CACHE_DIR/$MODEL_FILE" "$TARGET_DIR/"
    echo "文件已复制到: $TARGET_DIR/$MODEL_FILE"
    
    # 验证文件大小
    CACHE_SIZE=$(stat -f%z "$CACHE_DIR/$MODEL_FILE")
    TARGET_SIZE=$(stat -f%z "$TARGET_DIR/$MODEL_FILE")
    
    if [ "$CACHE_SIZE" -eq "$TARGET_SIZE" ]; then
        echo "文件验证成功，大小匹配: $TARGET_SIZE 字节"
        echo "布局检测模型修复成功！"
    else
        echo "警告: 复制的文件大小不匹配"
        echo "缓存文件大小: $CACHE_SIZE 字节"
        echo "目标文件大小: $TARGET_SIZE 字节"
    fi
else
    echo "在modelscope缓存中找不到模型文件: $CACHE_DIR/$MODEL_FILE"
    echo "请尝试运行 python scripts/download_models.py 下载模型"
    
    # 尝试使用替代方法
    echo "尝试替代方法下载模型..."
    
    # 检查是否安装了huggingface_hub
    if ! pip show huggingface_hub > /dev/null; then
        echo "正在安装 huggingface_hub..."
        pip install huggingface_hub
    fi
    
    # 使用替代脚本下载
    if [ -f "src/download_layout_model_alternative.py" ]; then
        echo "运行替代下载脚本..."
        python src/download_layout_model_alternative.py
    else
        echo "替代下载脚本不存在，请手动下载模型文件"
    fi
fi

# 3. 最终检查
if [ -f "$TARGET_DIR/$MODEL_FILE" ]; then
    echo "模型文件已就位: $TARGET_DIR/$MODEL_FILE"
    echo "现在应该可以正常使用布局检测功能了！"
else
    echo "模型文件仍然缺失，请尝试以下操作："
    echo "1. 手动访问 https://huggingface.co/juliozhao/DocLayout-YOLO-DocStructBench"
    echo "2. 下载 'doclayout_yolo_docstructbench_imgsz1024.pt' 文件"
    echo "3. 将下载的文件放置在 '$TARGET_DIR/' 目录下"
    echo "4. 将文件重命名为 '$MODEL_FILE'"
fi

echo "=== 修复过程完成 ===" 