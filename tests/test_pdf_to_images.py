#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import base64
import requests
from PIL import Image
import io
import argparse
import rootutils

ROOT_DIR = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)


def test_pdf_to_images_base64(pdf_path, dpi=200, output_format="png"):
    """测试PDF转图像API（返回Base64编码图像）

    Args:
        pdf_path: PDF文件路径
        dpi: 图像DPI
        output_format: 输出格式，png或jpg
    
    Returns:
        bool: 成功或失败
    """
    print(f"\n测试 PDF转图像API (Base64版)")
    print(f"PDF文件: {pdf_path}")
    print(f"参数: DPI={dpi}, 格式={output_format}")
    
    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误: 文件 {pdf_path} 不存在")
        return False
    
    # 准备文件和参数
    files = {'file': open(pdf_path, 'rb')}
    params = {
        'dpi': dpi,
        'output_format': output_format
    }
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 发送API请求
        response = requests.post(
            'http://localhost:8000/api/v1/pdf-to-images',
            files=files,
            data=params
        )
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        
        # 解析返回的JSON数据
        data = response.json()
        
        if data['success']:
            print(f"转换成功！共 {data['results']['page_count']} 页")
            print(f"响应时间: {elapsed_time:.2f} 秒")
            
            # 保存返回的图像
            images = data['results']['images']
            output_dir = os.path.join(ROOT_DIR, "data/outputs/pdf_to_images_test")
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"\n保存图像到: {output_dir}")
            for i, img_data in enumerate(images):
                # 将Base64字符串转换为图像
                img_bytes = base64.b64decode(img_data['data'])
                img = Image.open(io.BytesIO(img_bytes))
                
                # 保存图像
                output_path = os.path.join(output_dir, f"page_{i+1}.{output_format}")
                img.save(output_path)
                print(f"- 第 {i+1} 页: {output_path}")
            
            return True
        else:
            print(f"转换失败: {data['message']}")
            return False
    
    except Exception as e:
        print(f"处理响应时出错: {e}")
        return False
    finally:
        files['file'].close()


def test_pdf_to_images_save(pdf_path, dpi=300, output_format="png"):
    """测试PDF转图像API（将图像保存到服务器）

    Args:
        pdf_path: PDF文件路径
        dpi: 图像DPI
        output_format: 输出格式，png或jpg
    
    Returns:
        bool: 成功或失败
    """
    print(f"\n测试 PDF转图像API (持久化版)")
    print(f"PDF文件: {pdf_path}")
    print(f"参数: DPI={dpi}, 格式={output_format}")
    
    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误: 文件 {pdf_path} 不存在")
        return False
    
    # 准备文件和参数
    files = {'file': open(pdf_path, 'rb')}
    params = {
        'dpi': dpi,
        'output_format': output_format
    }
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 发送API请求
        response = requests.post(
            'http://localhost:8000/api/v1/pdf-to-images-save',
            files=files,
            data=params
        )
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        
        # 解析返回的JSON数据
        data = response.json()
        
        if data['success']:
            print(f"转换成功！共 {data['results']['page_count']} 页")
            print(f"响应时间: {elapsed_time:.2f} 秒")
            print(f"输出目录: {data['results']['output_dir']}")
            
            # 显示所有图像路径
            print("\n图像文件路径:")
            for i, path in enumerate(data['results']['image_paths']):
                print(f"- 第 {i+1} 页: {path}")
            
            return True
        else:
            print(f"转换失败: {data['message']}")
            return False
    
    except Exception as e:
        print(f"处理响应时出错: {e}")
        return False
    finally:
        files['file'].close()


def test_performance(pdf_path):
    """测试不同参数下的性能

    Args:
        pdf_path: PDF文件路径
    """
    print("\n性能测试 - 不同DPI和格式下的响应时间")
    
    # 定义要测试的不同参数组合
    test_params = [
        {'dpi': 100, 'output_format': 'png'},
        {'dpi': 200, 'output_format': 'png'},
        {'dpi': 300, 'output_format': 'png'},
        {'dpi': 200, 'output_format': 'jpg'}
    ]
    
    results = []
    
    # 对每组参数进行测试
    for params in test_params:
        print(f"\n测试参数: DPI={params['dpi']}, 格式={params['output_format']}")
        
        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            print(f"错误: 文件 {pdf_path} 不存在")
            break
        
        # 准备文件和参数
        files = {'file': open(pdf_path, 'rb')}
        
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 发送API请求
            response = requests.post(
                'http://localhost:8000/api/v1/pdf-to-images',
                files=files,
                data=params
            )
            
            # 计算耗时
            elapsed_time = time.time() - start_time
            
            # 解析返回的JSON数据
            data = response.json()
            
            if data['success']:
                print(f"转换成功！共 {data['results']['page_count']} 页")
                print(f"响应时间: {elapsed_time:.2f} 秒")
                
                results.append({
                    'dpi': params['dpi'],
                    'format': params['output_format'],
                    'pages': data['results']['page_count'],
                    'time': elapsed_time
                })
            else:
                print(f"转换失败: {data['message']}")
        
        except Exception as e:
            print(f"处理响应时出错: {e}")
        finally:
            files['file'].close()
    
    # 打印性能测试结果表格
    if results:
        print("\n性能测试结果:")
        print("-" * 50)
        print(f"{'DPI':<10}{'格式':<10}{'页数':<10}{'耗时(秒)':<10}")
        print("-" * 50)
        for r in results:
            print(f"{r['dpi']:<10}{r['format']:<10}{r['pages']:<10}{r['time']:.2f}")
        print("-" * 50)


def main():
    # 硬编码参数
    pdf_path = os.path.join(ROOT_DIR, "data/test.pdf")
    dpi = 200
    output_format = "png"
    mode = "all"  # 可选: 'base64', 'save', 'perf', 'all'
    
    print(f"使用PDF文件: {pdf_path}")
    
    # 检查默认路径文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误: PDF文件不存在，请确认路径: {pdf_path}")
        return
    
    # 根据模式运行测试
    if mode == 'all' or mode == 'base64':
        test_pdf_to_images_base64(pdf_path, dpi, output_format)
        
    if mode == 'all' or mode == 'save':
        test_pdf_to_images_save(pdf_path, dpi, output_format)
        
    if mode == 'all' or mode == 'perf':
        test_performance(pdf_path)


if __name__ == '__main__':
    main() 