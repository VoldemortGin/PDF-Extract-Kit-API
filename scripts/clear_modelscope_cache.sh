#!/bin/bash

# 脚本用于清理modelscope缓存目录
# 作者: ChatGPT
# 日期: 2025-05-02

echo "=== 开始清理ModelScope缓存 ==="

# 先检查项目目录中的模型文件是否完整
MODEL_COUNT=$(find models -name "*.pt" | wc -l)
MODEL_SIZE=$(du -sh models/ | cut -f1)
CACHE_SIZE=$(du -sh ~/.cache/modelscope/ | cut -f1)

echo "项目目录中模型数量: $MODEL_COUNT"
echo "项目目录中模型大小: $MODEL_SIZE"
echo "缓存目录大小: $CACHE_SIZE"

if [ "$MODEL_COUNT" -lt 3 ]; then
    echo "警告: 项目目录中可能缺少关键模型文件。首先运行 python -m scripts.download_models 确保所有模型已复制到项目目录。"
    read -p "是否继续删除缓存? (y/n): " CONFIRM
    if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
        echo "取消操作，退出脚本。"
        exit 1
    fi
fi

# 保存要删除的目录列表
CACHE_DIRS=(
    ~/.cache/modelscope/hub/models/opendatalab/PDF-Extract-Kit-1___0
    ~/.cache/modelscope/hub/models/opendatalab/PDF-Extract-Kit-1.0
    ~/.cache/modelscope/hub/models/ppaanngggg/layoutreader
)

# 执行删除
echo "正在删除ModelScope缓存目录..."
for DIR in "${CACHE_DIRS[@]}"; do
    if [ -d "$DIR" ]; then
        echo "删除目录: $DIR"
        rm -rf "$DIR"
    else
        echo "目录不存在，跳过: $DIR"
    fi
done

# 检查结果
NEW_CACHE_SIZE=$(du -sh ~/.cache/modelscope/ 2>/dev/null | cut -f1 || echo "0")
echo "清理前缓存大小: $CACHE_SIZE"
echo "清理后缓存大小: $NEW_CACHE_SIZE"
echo "=== 清理完成 ===" 