#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests
import argparse
import hashlib
from tqdm import tqdm
import rootutils

ROOT_DIR = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

# 获取HuggingFace token
HF_TOKEN = os.environ.get("HF_TOKEN", None)

MODEL_CONFIGS = {
    "layout_detection": {
        "name": "布局检测模型",
        "files": [
            {
                "url": "https://huggingface.co/BAAI/YOLO-Layout/resolve/main/doclayout_yolo_ft.pt",
                "path": "models/Layout/YOLO/doclayout_yolo_ft.pt",
                "md5": None,  # 如果有md5校验码可以填入
            }
        ]
    },
    "formula_detection": {
        "name": "公式检测模型",
        "files": [
            {
                "url": "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt",
                "path": "models/FormDetect/yolo8m.pt",
                "md5": None,
            }
        ]
    },
    "formula_recognition": {
        "name": "公式识别模型",
        "files": [
            {
                "url": "https://huggingface.co/facebook/nougat-base/resolve/main/pytorch_model.bin",
                "path": "models/Nougat/pytorch_model.bin",
                "md5": None,
            },
            {
                "url": "https://huggingface.co/facebook/nougat-base/resolve/main/config.json",
                "path": "models/Nougat/config.json",
                "md5": None,
            },
            {
                "url": "https://huggingface.co/facebook/nougat-base/resolve/main/tokenizer_config.json",
                "path": "models/Nougat/tokenizer_config.json",
                "md5": None,
            },
            {
                "url": "https://huggingface.co/facebook/nougat-base/resolve/main/tokenizer.json",
                "path": "models/Nougat/tokenizer.json",
                "md5": None,
            }
        ]
    },
    "table_parsing": {
        "name": "表格解析模型",
        "files": [
            {
                "url": "https://drive.google.com/uc?export=download&id=1-xm9A9Qw0t4PTAZhynJDCm0gWZqCUAYf",
                "path": "models/CascadeTabNet/cascade_mask_rcnn_hrnetv2p_w32_20e.pth",
                "md5": None,
            },
            {
                "url": "https://drive.google.com/uc?export=download&id=1-yx-Cm2Z0WKfLMTHrJVjW7wCXQYLWo8P",
                "path": "models/CascadeTabNet/cell_cls_model.pth",
                "md5": None,
            }
        ]
    }
}


def check_md5(file_path, md5):
    """检查文件的MD5是否匹配。
    
    Args:
        file_path (str): 文件路径
        md5 (str): 预期的MD5值
    
    Returns:
        bool: 如果MD5匹配或不需要验证则返回True，否则返回False
    """
    if md5 is None:
        return True
    
    with open(file_path, 'rb') as f:
        file_md5 = hashlib.md5(f.read()).hexdigest()
    
    return file_md5 == md5


def download_from_google_drive(file_id, save_path, chunk_size=32768):
    """从Google Drive下载文件。
    
    Args:
        file_id (str): Google Drive文件ID
        save_path (str): 保存路径
        chunk_size (int): 分块大小
    
    Returns:
        bool: 下载成功返回True，否则返回False
    """
    try:
        # 创建保存目录
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        session = requests.Session()
        
        # 第一次请求获取确认token
        response = session.get(url, stream=True)
        response.raise_for_status()
        
        # 检查是否需要确认
        for k, v in response.cookies.items():
            if k.startswith('download_warning'):
                # 添加确认token
                url = f"{url}&confirm={v}"
                break
        
        # 第二次请求下载实际文件
        response = session.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        print(f"下载文件: Google Drive ID {file_id}")
        print(f"保存到: {save_path}")
        
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))
        
        progress_bar.close()
        return True
    
    except Exception as e:
        print(f"从Google Drive下载失败: {str(e)}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return False


def download_file(url, save_path, chunk_size=8192):
    """下载文件并显示进度条。
    
    Args:
        url (str): 下载URL
        save_path (str): 保存路径
        chunk_size (int): 分块大小
    
    Returns:
        bool: 下载成功返回True，否则返回False
    """
    try:
        # 检查是否为Google Drive链接
        if "drive.google.com" in url:
            # 提取Google Drive文件ID
            if "id=" in url:
                file_id = url.split("id=")[1].split("&")[0]
                return download_from_google_drive(file_id, save_path)
            else:
                print(f"无法从URL中提取Google Drive文件ID: {url}")
                return False
        
        # 创建保存目录
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 准备请求头
        headers = {}
        # 如果是HuggingFace链接且有token，添加认证头
        if "huggingface.co" in url and HF_TOKEN:
            headers["Authorization"] = f"Bearer {HF_TOKEN}"
        
        # 下载文件
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        print(f"下载文件: {url}")
        print(f"保存到: {save_path}")
        
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))
        
        progress_bar.close()
        return True
    
    except Exception as e:
        print(f"下载失败: {str(e)}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return False


def download_models(model_types=None, force=False):
    """下载指定类型的模型。
    
    Args:
        model_types (list): 要下载的模型类型列表，默认为None表示下载所有模型
        force (bool): 是否强制重新下载已存在的模型
    """
    if model_types is None:
        # 下载所有模型
        model_types = list(MODEL_CONFIGS.keys())
    
    for model_type in model_types:
        if model_type not in MODEL_CONFIGS:
            print(f"未知的模型类型: {model_type}")
            continue
        
        model_config = MODEL_CONFIGS[model_type]
        print(f"\n>>> 开始下载{model_config['name']}...")
        
        for file_info in model_config['files']:
            url = file_info['url']
            save_path = os.path.join(ROOT_DIR, file_info['path'])
            md5 = file_info['md5']
            
            # 检查文件是否已存在且有效
            if os.path.exists(save_path) and not force:
                if check_md5(save_path, md5):
                    print(f"文件已存在且有效，跳过下载: {save_path}")
                    continue
                else:
                    print(f"文件存在但MD5校验失败，重新下载: {save_path}")
            
            # 下载文件
            success = download_file(url, save_path)
            
            if success:
                # 校验MD5
                if md5 is not None and not check_md5(save_path, md5):
                    print(f"警告: 文件MD5校验失败，可能下载损坏: {save_path}")
                else:
                    print(f"成功下载: {save_path}")
            else:
                print(f"下载失败: {url}")
    
    print("\n>>> 所有下载任务完成")


def main():
    """主函数，处理命令行参数并执行下载。"""
    parser = argparse.ArgumentParser(description='下载PDF-Extract-Kit所需模型文件')
    parser.add_argument('--models', nargs='+', choices=list(MODEL_CONFIGS.keys()) + ['all'],
                       help='要下载的模型类型，可以指定多个，或使用"all"下载所有模型')
    parser.add_argument('--force', action='store_true', help='是否强制重新下载已存在的模型')
    
    args = parser.parse_args()
    
    if args.models is None or 'all' in args.models:
        model_types = None  # 下载所有模型
    else:
        model_types = args.models
    
    download_models(model_types, args.force)


if __name__ == '__main__':
    main() 