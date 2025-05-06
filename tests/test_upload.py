#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import base64
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import rootutils

ROOT_DIR = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

# 导入主应用
from main import app

# 创建测试客户端
client = TestClient(app)

# 测试文件路径
TEST_PDF_PATH = os.path.join(ROOT_DIR, "data/GB-4660-2016-机动车用前雾灯配光性能.pdf")
TEST_DOCX_PATH = os.path.join(ROOT_DIR, "data/GB-4660-2016-机动车用前雾灯配光性能.docx")


def test_upload_pdf_file():
    """测试上传PDF文件。
    
    检查上传PDF文件是否成功，并验证响应中包含正确的文件信息。
    """
    # 确保测试文件存在
    assert os.path.exists(TEST_PDF_PATH), f"测试PDF文件不存在: {TEST_PDF_PATH}"
    
    # 准备上传文件
    with open(TEST_PDF_PATH, "rb") as f:
        files = {"file": (os.path.basename(TEST_PDF_PATH), f, "application/pdf")}
        
        # 发送请求
        response = client.post("/api/v1/upload", files=files)
        
        # 验证状态码
        assert response.status_code == 200
        
        # 解析响应
        data = response.json()
        
        # 验证响应内容
        assert data["success"] is True
        assert data["message"] == "文件上传成功"
        assert data["file_name"] == os.path.basename(TEST_PDF_PATH)
        assert data["file_type"] == "pdf"
        assert "file_data" in data
        assert len(data["file_data"]) > 0


def test_upload_unsupported_file():
    """测试上传不支持的文件类型。
    
    检查上传不支持的文件类型时是否返回正确的错误响应。
    """
    # 确保测试文件存在
    assert os.path.exists(TEST_DOCX_PATH), f"测试DOCX文件不存在: {TEST_DOCX_PATH}"
    
    # 准备上传文件
    with open(TEST_DOCX_PATH, "rb") as f:
        files = {"file": (os.path.basename(TEST_DOCX_PATH), f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        
        # 发送请求
        response = client.post("/api/v1/upload", files=files)
        
        # 验证状态码
        assert response.status_code == 400
        
        # 解析响应
        data = response.json()
        
        # 验证错误消息
        assert "不支持的文件类型" in data["detail"]


def test_upload_empty_file():
    """测试上传空文件。
    
    检查未提供文件时是否返回正确的错误响应。
    """
    # 发送空请求
    response = client.post("/api/v1/upload")
    
    # 验证状态码
    assert response.status_code in [400, 422]  # FastAPI可能返回400或422


def test_upload_image_file():
    """测试上传图像文件。
    
    创建临时图像文件并测试上传，验证响应中包含正确的文件信息。
    """
    # 使用PIL创建一个临时图像文件
    from PIL import Image
    import tempfile
    
    # 创建临时目录
    temp_dir = os.path.join(ROOT_DIR, "data/temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # 创建一个简单的测试图像
    temp_image_path = os.path.join(temp_dir, "test_image.png")
    try:
        # 创建一个简单的测试图像
        img = Image.new('RGB', (100, 100), color='red')
        img.save(temp_image_path)
        
        # 准备上传文件
        with open(temp_image_path, "rb") as f:
            files = {"file": ("test_image.png", f, "image/png")}
            
            # 发送请求
            response = client.post("/api/v1/upload", files=files)
            
            # 验证状态码
            assert response.status_code == 200
            
            # 解析响应
            data = response.json()
            
            # 验证响应内容
            assert data["success"] is True
            assert data["message"] == "文件上传成功"
            assert data["file_name"] == "test_image.png"
            assert data["file_type"] == "png"
            assert "file_data" in data
            assert len(data["file_data"]) > 0
    
    finally:
        # 清理临时文件
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)


if __name__ == "__main__":
    # 直接运行测试
    pytest.main(["-v", __file__]) 