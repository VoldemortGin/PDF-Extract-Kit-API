#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
import sys
from tqdm import tqdm
from huggingface_hub import hf_hub_download
import rootutils

ROOT_DIR = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

def download_alternative_model():
    """下载替代的布局检测模型。
    
    尝试从DocLayout-YOLO项目或其他可用源下载模型。
    """
    # 创建保存目录
    save_dir = os.path.join(ROOT_DIR, "models/Layout/YOLO")
    save_path = os.path.join(save_dir, "doclayout_yolo_ft.pt")
    os.makedirs(save_dir, exist_ok=True)
    
    print("开始下载替代布局检测模型...")
    
    # 方法1: 尝试从HuggingFace下载DocLayout-YOLO模型
    try:
        print("尝试从HuggingFace下载DocLayout-YOLO模型...")
        model_path = hf_hub_download(
            repo_id="juliozhao/DocLayout-YOLO-DocStructBench",
            filename="doclayout_yolo_docstructbench_imgsz1024.pt",
            local_dir=save_dir,
            local_dir_use_symlinks=False
        )
        
        # 如果下载成功但文件名不同，则复制或重命名为目标文件名
        if model_path and model_path != save_path:
            import shutil
            shutil.copy(model_path, save_path)
            print(f"模型已下载并复制到: {save_path}")
        
        return True
    except Exception as e:
        print(f"从HuggingFace下载模型失败: {str(e)}")
    
    # 方法2: 尝试直接从GitHub下载YOLO-doclaynet模型
    try:
        print("尝试从Huggingface通过HTTP直接下载模型...")
        url = "https://huggingface.co/juliozhao/DocLayout-YOLO-DocStructBench/resolve/main/doclayout_yolo_docstructbench_imgsz1024.pt"
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 获取文件大小
        total_size = int(response.headers.get('content-length', 0))
        
        # 显示下载进度
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)
        
        # 下载文件
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))
        
        progress_bar.close()
        print(f"成功下载模型到: {save_path}")
        return True
    except Exception as e:
        print(f"通过HTTP下载模型失败: {str(e)}")
    
    # 方法3: 尝试从其他可用源下载
    try:
        print("尝试从其他来源下载模型...")
        url = "https://huggingface.co/hantian/yolo-doclaynet/resolve/main/yolov8l.pt"
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 获取文件大小
        total_size = int(response.headers.get('content-length', 0))
        
        # 显示下载进度
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)
        
        # 下载文件
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))
        
        progress_bar.close()
        print(f"成功下载模型到: {save_path}")
        return True
    except Exception as e:
        print(f"从其他来源下载模型失败: {str(e)}")
    
    print("\n所有下载尝试都失败。")
    return False

if __name__ == "__main__":
    if not download_alternative_model():
        sys.exit(1) 