#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
from fastapi.testclient import TestClient
import tempfile
from PIL import Image
import rootutils

ROOT_DIR = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

# 导入主应用
from main import app


@pytest.fixture(scope="session")
def client():
    """创建测试客户端。
    
    Returns:
        TestClient: FastAPI测试客户端
    """
    return TestClient(app)


@pytest.fixture(scope="session")
def test_files():
    """创建测试所需的文件和目录。
    
    Returns:
        tuple: (pdf_path, image_path) 测试文件的路径
    """
    # 确保测试目录存在
    test_dir = os.path.join(ROOT_DIR, "data/test_files")
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建测试PDF文件（如果不存在）
    pdf_path = os.path.join(test_dir, "sample.pdf")
    if not os.path.exists(pdf_path):
        # 使用一个简单的PDF文件进行测试
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawString(100, 750, "测试PDF文档")
        c.drawString(100, 700, "包含一些文本和公式: E = mc²")
        c.save()
    
    # 创建测试图像文件（如果不存在）
    image_path = os.path.join(test_dir, "sample.png")
    if not os.path.exists(image_path):
        img = Image.new('RGB', (500, 300), color='white')
        # 添加文本
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("Arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "测试图像", fill="black", font=font)
        draw.text((50, 100), "包含一些文本", fill="black", font=font)
        img.save(image_path)
    
    return {"pdf": pdf_path, "image": image_path}


@pytest.fixture(scope="session")
def temp_directory():
    """创建临时目录。
    
    Yields:
        str: 临时目录路径
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def temp_text_file():
    """创建临时文本文件。
    
    Returns:
        str: 临时文本文件路径
    """
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp.write(b"This is a test text file")
        tmp_path = tmp.name
    
    yield tmp_path
    
    # 清理临时文件
    if os.path.exists(tmp_path):
        os.remove(tmp_path) 