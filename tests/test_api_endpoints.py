#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import pytest
import rootutils

ROOT_DIR = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)


def test_root(client):
    """测试根路径。"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "欢迎使用PDF-Extract-Kit API" in data["message"]


def test_health_check(client):
    """测试健康检查端点。"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_layout_detection(client, test_files):
    """测试布局检测API。"""
    # 准备上传文件
    with open(test_files["pdf"], "rb") as f:
        files = {"file": (os.path.basename(test_files["pdf"]), f, "application/pdf")}
        data = {
            "img_size": "1024",
            "conf_thres": "0.25",
            "iou_thres": "0.45",
            "visualize": "false"
        }
        
        # 发送请求
        response = client.post("/api/v1/layout-detection", files=files, data=data)
        
        # 验证状态码
        assert response.status_code == 200
        
        # 解析响应
        data = response.json()
        
        # 验证响应内容
        assert data["success"] is True
        assert "布局检测任务完成" in data["message"]


def test_ocr(client, test_files):
    """测试OCR API。"""
    # 准备上传文件
    with open(test_files["image"], "rb") as f:
        files = {"file": (os.path.basename(test_files["image"]), f, "image/png")}
        data = {
            "use_angle_cls": "true",
            "lang": "ch",
            "det": "true",
            "rec": "true",
            "cls": "true",
            "visualize": "false"
        }
        
        # 发送请求
        response = client.post("/api/v1/ocr", files=files, data=data)
        
        # 验证状态码
        assert response.status_code == 200
        
        # 解析响应
        data = response.json()
        
        # 验证响应内容
        assert data["success"] is True
        assert "OCR任务完成" in data["message"]


def test_formula_detection(client, test_files):
    """测试公式检测API。"""
    # 准备上传文件
    with open(test_files["pdf"], "rb") as f:
        files = {"file": (os.path.basename(test_files["pdf"]), f, "application/pdf")}
        data = {
            "img_size": "1024",
            "conf_thres": "0.25",
            "iou_thres": "0.45",
            "visualize": "false"
        }
        
        # 发送请求
        response = client.post("/api/v1/formula-detection", files=files, data=data)
        
        # 验证状态码
        assert response.status_code == 200
        
        # 解析响应
        data = response.json()
        
        # 验证响应内容
        assert data["success"] is True
        assert "公式检测任务完成" in data["message"]


def test_formula_recognition(client, test_files):
    """测试公式识别API。"""
    # 准备上传文件
    with open(test_files["pdf"], "rb") as f:
        files = {"file": (os.path.basename(test_files["pdf"]), f, "application/pdf")}
        data = {
            "beam_size": "5",
            "max_seq_length": "400",
            "visualize": "false"
        }
        
        # 发送请求
        response = client.post("/api/v1/formula-recognition", files=files, data=data)
        
        # 验证状态码
        assert response.status_code == 200
        
        # 解析响应
        data = response.json()
        
        # 验证响应内容
        assert data["success"] is True
        assert "公式识别任务完成" in data["message"]


def test_table_parsing(client, test_files):
    """测试表格解析API。"""
    # 准备上传文件
    with open(test_files["pdf"], "rb") as f:
        files = {"file": (os.path.basename(test_files["pdf"]), f, "application/pdf")}
        data = {
            "visualize": "false"
        }
        
        # 发送请求
        response = client.post("/api/v1/table-parsing", files=files, data=data)
        
        # 验证状态码
        assert response.status_code == 200
        
        # 解析响应
        data = response.json()
        
        # 验证响应内容
        assert data["success"] is True
        assert "表格解析任务完成" in data["message"]


def test_pdf2markdown(client, test_files):
    """测试PDF转Markdown API。"""
    # 准备上传文件
    with open(test_files["pdf"], "rb") as f:
        files = {"file": (os.path.basename(test_files["pdf"]), f, "application/pdf")}
        data = {
            "merge2markdown": "true"
        }
        
        # 发送请求
        response = client.post("/api/v1/pdf2markdown", files=files, data=data)
        
        # 验证状态码
        assert response.status_code == 200
        
        # 解析响应
        data = response.json()
        
        # 验证响应内容
        assert data["success"] is True
        assert "PDF转Markdown任务完成" in data["message"]
        # 检查results中是否有markdown字段
        if data["success"]:
            assert "results" in data
            if data["results"]:
                assert "markdown" in data["results"]


def test_run_project(client, test_files):
    """测试运行项目API。"""
    # 准备上传文件
    with open(test_files["pdf"], "rb") as f:
        files = {"file": (os.path.basename(test_files["pdf"]), f, "application/pdf")}
        # 创建简单配置
        config_content = """
        tasks:
          layout_detection:
            model: layout_detection_yolo
            model_config:
              model_path: models/Layout/YOLO/doclayout_yolo_ft.pt
        """
        data = {
            "config_content": config_content
        }
        
        # 发送请求
        response = client.post("/api/v1/run-project", files=files, data=data)
        
        # 验证状态码
        assert response.status_code == 200
        
        # 解析响应
        data = response.json()
        
        # 验证响应内容
        assert data["success"] is True
        assert "项目运行完成" in data["message"]


def test_pdf_to_images(client, test_files):
    """测试PDF转图像API。"""
    # 准备上传文件
    with open(test_files["pdf"], "rb") as f:
        files = {"file": (os.path.basename(test_files["pdf"]), f, "application/pdf")}
        data = {
            "dpi": "200",
            "output_format": "png"
        }
        
        # 发送请求
        response = client.post("/api/v1/pdf-to-images", files=files, data=data)
        
        # 验证状态码
        assert response.status_code == 200
        
        # 解析响应
        data = response.json()
        
        # 验证响应内容
        assert data["success"] is True
        assert "PDF转图像任务完成" in data["message"]
        if data["success"] and data["results"]:
            assert "images" in data["results"]


def test_pdf_to_images_save(client, test_files):
    """测试PDF转图像并保存API。"""
    # 准备上传文件
    with open(test_files["pdf"], "rb") as f:
        files = {"file": (os.path.basename(test_files["pdf"]), f, "application/pdf")}
        data = {
            "dpi": "200",
            "output_format": "png"
        }
        
        # 发送请求
        response = client.post("/api/v1/pdf-to-images-save", files=files, data=data)
        
        # 验证状态码
        assert response.status_code == 200
        
        # 解析响应
        data = response.json()
        
        # 验证响应内容
        assert data["success"] is True
        assert "PDF转图像并保存任务完成" in data["message"]
        if data["success"] and data["results"]:
            assert "file_paths" in data["results"]


def test_upload_api(client, test_files, temp_text_file):
    """测试文件上传API。"""
    # 测试上传PDF文件
    with open(test_files["pdf"], "rb") as f:
        files = {"file": (os.path.basename(test_files["pdf"]), f, "application/pdf")}
        response = client.post("/api/v1/upload", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "文件上传成功"
        assert data["file_name"] == os.path.basename(test_files["pdf"])
        assert data["file_type"] == "pdf"
        assert "file_data" in data
        assert len(data["file_data"]) > 0
    
    # 测试上传图像文件
    with open(test_files["image"], "rb") as f:
        files = {"file": (os.path.basename(test_files["image"]), f, "image/png")}
        response = client.post("/api/v1/upload", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "文件上传成功"
        assert data["file_name"] == os.path.basename(test_files["image"])
        assert data["file_type"] == "png"
        assert "file_data" in data
        assert len(data["file_data"]) > 0
    
    # 测试上传不支持的文件类型
    with open(temp_text_file, "rb") as f:
        files = {"file": (os.path.basename(temp_text_file), f, "text/plain")}
        response = client.post("/api/v1/upload", files=files)
        assert response.status_code == 400
        data = response.json()
        assert "不支持的文件类型" in data["detail"]


def test_custom_functions(temp_directory):
    """测试辅助函数文件的功能。
    
    通过编写针对这些辅助函数的测试，我们可以确保它们按预期工作。
    """
    # 测试临时文件创建和读取
    temp_file = os.path.join(temp_directory, "test.txt")
    with open(temp_file, "w") as f:
        f.write("测试内容")
    assert os.path.exists(temp_file)
    with open(temp_file, "r") as f:
        content = f.read()
    assert content == "测试内容"


if __name__ == "__main__":
    # 直接运行测试
    pytest.main(["-v", __file__]) 