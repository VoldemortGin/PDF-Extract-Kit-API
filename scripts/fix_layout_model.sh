#!/bin/bash

# 脚本用于修复布局检测模型问题
# 作者: ChatGPT
# 日期: 2023-10-17

echo "=== 开始修复布局检测模型问题 ==="

# 1. 安装必要的依赖
echo "正在安装必要的依赖..."
pip install huggingface_hub

# 2. 下载替代模型
echo "正在下载替代的布局检测模型..."
python src/download_layout_model_alternative.py

# 3. 检查模型是否已成功下载
if [ -f "models/Layout/YOLO/doclayout_yolo_ft.pt" ]; then
    echo "模型已成功下载，文件位置: models/Layout/YOLO/doclayout_yolo_ft.pt"
    echo "现在应该可以正常使用布局检测功能了！"
else
    echo "模型下载失败，请尝试以下操作："
    echo "1. 手动访问 https://huggingface.co/juliozhao/DocLayout-YOLO-DocStructBench"
    echo "2. 下载 'doclayout_yolo_docstructbench_imgsz1024.pt' 文件"
    echo "3. 将下载的文件放置在 'models/Layout/YOLO/' 目录下"
    echo "4. 将文件重命名为 'doclayout_yolo_ft.pt'"
fi

echo "=== 修复过程完成 ===" 