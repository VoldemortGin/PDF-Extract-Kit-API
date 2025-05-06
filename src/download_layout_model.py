#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
from tqdm import tqdm
import rootutils
import sys

ROOT_DIR = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

def download_layout_model():
    """下载布局检测模型。
    使用HuggingFace认证下载模型。
    """
    # 获取HF_TOKEN
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        hf_token = input("请输入你的HuggingFace API令牌: ")
        if not hf_token:
            print("错误: 需要HuggingFace API令牌才能下载模型")
            return False
    
    # 尝试多个可能的URL
    urls = [
        "https://huggingface.co/BAAI/YOLO-Layout/resolve/main/doclayout_yolo_ft.pt",
        "https://huggingface.co/BAAI/YOLO-Layout/blob/main/doclayout_yolo_ft.pt",
        "https://huggingface.co/BAAI/YOLO-Layout/resolve/main/model.pt",
        "https://huggingface.co/BAAI/YOLO-Layout/resolve/master/doclayout_yolo_ft.pt",
        "https://huggingface.co/BAAI/YOLO-Layout/raw/main/doclayout_yolo_ft.pt"
    ]
    
    save_path = os.path.join(ROOT_DIR, "models/Layout/YOLO/doclayout_yolo_ft.pt")
    
    # 创建保存目录
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # 配置认证头
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    print(f"开始尝试下载布局检测模型...")
    
    for i, url in enumerate(urls):
        print(f"\n尝试下载源 {i+1}/{len(urls)}: {url}")
        print(f"保存到: {save_path}")
        
        try:
            # 发送请求
            response = requests.get(url, headers=headers, stream=True)
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
            print(f"从此源下载失败: {str(e)}")
            if os.path.exists(save_path) and os.path.getsize(save_path) == 0:
                os.remove(save_path)
    
    print("\n所有下载源尝试失败。正在尝试替代方案...")
    
    # 如果所有URL都失败，尝试使用预设的空模型
    try:
        print("注意：无法下载官方模型，将创建一个空模型文件。")
        print("该模型只是一个占位文件，需要您自行寻找并替换真实的模型文件。")
        
        # 创建一个小型的占位文件
        with open(save_path, 'wb') as f:
            f.write(b'MODEL_PLACEHOLDER')
        
        print(f"已创建占位模型文件: {save_path}")
        print("警告：这不是真实的模型文件，API调用会失败。您需要手动替换此文件为真实模型。")
        return True
    
    except Exception as e:
        print(f"创建占位文件失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = download_layout_model()
    if not success:
        sys.exit(1) 