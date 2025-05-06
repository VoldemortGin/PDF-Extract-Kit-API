import json
import os
import shutil

import requests
from modelscope import snapshot_download


def download_json(url):
    # 下载JSON文件
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功
    return response.json()


def download_and_modify_json(url, local_filename, modifications):
    if os.path.exists(local_filename):
        data = json.load(open(local_filename))
        config_version = data.get('config_version', '0.0.0')
        if config_version < '1.1.1':
            data = download_json(url)
    else:
        data = download_json(url)

    # 修改内容
    for key, value in modifications.items():
        data[key] = value

    # 保存修改后的内容
    with open(local_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def copy_model_to_project_dir(cache_dir, target_dir):
    """
    将缓存中的模型复制到项目目录
    
    Args:
        cache_dir: 缓存目录
        target_dir: 目标目录
    """
    # 创建目标根目录
    os.makedirs(target_dir, exist_ok=True)
    
    # 复制模型文件
    print(f"正在将模型文件从缓存目录复制到项目目录: {target_dir}")
    
    if os.path.exists(cache_dir):
        # 复制整个models目录
        for root, dirs, files in os.walk(cache_dir):
            # 计算相对路径，用于构建目标路径
            rel_path = os.path.relpath(root, cache_dir)
            target_path = os.path.join(target_dir, rel_path) if rel_path != "." else target_dir
            
            # 创建目标目录
            os.makedirs(target_path, exist_ok=True)
            
            # 复制文件
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_path, file)
                
                # 如果目标文件已存在且大小相同，则跳过
                if os.path.exists(dst_file) and os.path.getsize(src_file) == os.path.getsize(dst_file):
                    print(f"文件已存在且大小相同，跳过复制: {dst_file}")
                    continue
                
                shutil.copy2(src_file, dst_file)
                print(f"已复制文件: {dst_file}")
    
    print("模型复制完成!")


if __name__ == '__main__':
    # 项目根目录下的models目录
    project_models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    
    # 定义要下载的模型路径模式
    mineru_patterns = [
        "models/Layout/LayoutLMv3/*",
        "models/Layout/YOLO/*",
        "models/MFD/YOLO/*",
        "models/MFR/unimernet_small_2501/*",
        "models/TabRec/TableMaster/*",
        "models/TabRec/StructEqTable/*",
    ]
    
    # 下载模型到缓存目录
    print("正在下载模型到缓存目录...")
    model_dir = snapshot_download('opendatalab/PDF-Extract-Kit-1.0', allow_patterns=mineru_patterns)
    layoutreader_model_dir = snapshot_download('ppaanngggg/layoutreader')
    
    # 缓存中的模型目录
    cache_models_dir = model_dir + '/models'
    print(f'缓存模型目录: {cache_models_dir}')
    print(f'布局识别模型目录: {layoutreader_model_dir}')
    
    # 将模型从缓存复制到项目目录
    copy_model_to_project_dir(cache_models_dir, project_models_dir)
    
    # 创建和修改配置文件
    json_url = 'https://gcore.jsdelivr.net/gh/opendatalab/MinerU@master/magic-pdf.template.json'
    config_file_name = 'magic-pdf.json'
    home_dir = os.path.expanduser('~')
    config_file = os.path.join(home_dir, config_file_name)
    
    # 使用项目目录中的模型路径
    json_mods = {
        'models-dir': project_models_dir,
        'layoutreader-model-dir': layoutreader_model_dir,
    }
    
    download_and_modify_json(json_url, config_file, json_mods)
    print(f'配置文件已成功配置，路径为: {config_file}')
    print(f'模型已下载并复制到项目目录: {project_models_dir}')
