import os
import uuid
import importlib.util
import tempfile
import base64
import json
import shutil
from typing import Dict, List, Union

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import yaml

import rootutils

ROOT_DIR = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

try:
    from pdf_extract_kit.utils.config_loader import load_config, initialize_tasks_and_models
    import pdf_extract_kit.tasks
    PDF_EXTRACT_KIT_AVAILABLE = True
except ImportError:
    PDF_EXTRACT_KIT_AVAILABLE = False

from src.api.models import (
    TaskResponse,
    LayoutDetectionRequest,
    OCRRequest,
    FormulaDetectionRequest,
    FormulaRecognitionRequest,
    TableParsingRequest,
    PDF2MarkdownRequest,
    RunProjectRequest,
    Base64Image,
    PDFToImagesRequest,
)
from src.api.utils import ensure_data_dir, save_upload_file_temp, encode_image_to_base64, cleanup_temp_dir, convert_pdf_to_images

router = APIRouter()

# 检查某个模块是否可用
def check_module_available(module_name):
    return importlib.util.find_spec(module_name) is not None


@router.post("/layout-detection", response_model=TaskResponse)
async def layout_detection(
    file: UploadFile = File(...),
    img_size: int = Form(1024),
    conf_thres: float = Form(0.25),
    iou_thres: float = Form(0.45),
    visualize: bool = Form(False)
) -> Dict:
    """布局检测API。临时处理文件，不保存在服务器上。
    
    Args:
        file: 要上传的PDF或图像文件
        img_size: 图像大小
        conf_thres: 置信度阈值
        iou_thres: IOU阈值
        visualize: 是否可视化结果
    
    Returns:
        TaskResponse: 任务响应
    """
    temp_dir = None
    
    try:
        # 保存上传的文件到临时目录
        temp_dir, temp_file = await save_upload_file_temp(file)
        
        # 创建临时输出目录
        temp_output_dir = os.path.join(temp_dir, "output")
        os.makedirs(temp_output_dir, exist_ok=True)
        
        # 创建配置
        config = {
            "inputs": temp_file,
            "outputs": temp_output_dir,
            "tasks": {
                "layout_detection": {
                    "model": "layout_detection_yolo",
                    "model_config": {
                        "img_size": img_size,
                        "conf_thres": conf_thres,
                        "iou_thres": iou_thres,
                        "model_path": "models/Layout/YOLO/doclayout_yolo_ft.pt",
                        "visualize": visualize
                    }
                }
            }
        }
        
        # 初始化任务和模型
        task_instances = initialize_tasks_and_models(config)
        
        # 执行任务
        model = task_instances["layout_detection"]
        model_results = model.predict_images(temp_file, temp_output_dir)
        
        # 获取id_to_names映射
        id_to_names = {
            0: 'title', 
            1: 'plain text',
            2: 'abandon', 
            3: 'figure', 
            4: 'figure_caption', 
            5: 'table', 
            6: 'table_caption', 
            7: 'table_footnote', 
            8: 'isolate_formula', 
            9: 'formula_caption'
        }
        
        # 将YOLO模型结果转换为可序列化格式
        results = []
        for res in model_results:
            if hasattr(res, '__dict__'):
                # 获取YOLO结果的boxes, classes, scores
                boxes = res.__dict__['boxes'].xyxy.tolist() if hasattr(res.__dict__['boxes'], 'xyxy') else []
                classes = res.__dict__['boxes'].cls.tolist() if hasattr(res.__dict__['boxes'], 'cls') else []
                scores = res.__dict__['boxes'].conf.tolist() if hasattr(res.__dict__['boxes'], 'conf') else []
                
                # 构建结构化的检测结果
                detections = []
                for i in range(len(boxes)):
                    if i < len(classes) and i < len(scores):
                        detections.append({
                            "box": boxes[i],
                            "class": int(classes[i]),
                            "class_name": id_to_names.get(int(classes[i]), "unknown"),
                            "score": float(scores[i])
                        })
                
                results.append({
                    "detections": detections
                })
            else:
                # 如果结果已经是字典格式，直接添加
                results.append(res)
        
        # 如果生成了可视化结果，则转换为Base64
        if visualize:
            # 查找可视化图像文件
            visualization_results = []
            for root, _, files in os.walk(temp_output_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)
                        base64_data = encode_image_to_base64(img_path)
                        visualization_results.append(base64_data)
            
            # 添加可视化结果到返回数据
            if results:
                results[0]["visualizations"] = visualization_results
        
        return {
            "success": True,
            "message": "布局检测任务完成",
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"布局检测任务失败: {str(e)}",
            "results": None
        }
    finally:
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            cleanup_temp_dir(temp_dir)


@router.post("/ocr", response_model=TaskResponse)
async def ocr(
    file: UploadFile = File(...),
    use_angle_cls: bool = Form(True),
    lang: str = Form("ch"),
    det: bool = Form(True),
    rec: bool = Form(True),
    cls: bool = Form(True),
    visualize: bool = Form(False)
) -> Dict:
    """OCR文字识别API。临时处理文件，不保存在服务器上。
    
    Args:
        file: 要上传的PDF或图像文件
        use_angle_cls: 是否使用角度分类
        lang: 语言
        det: 是否进行检测
        rec: 是否进行识别
        cls: 是否进行分类
        visualize: 是否可视化结果
    
    Returns:
        TaskResponse: 任务响应
    """
    temp_dir = None
    
    try:
        # 保存上传的文件到临时目录
        temp_dir, temp_file = await save_upload_file_temp(file)
        
        # 创建临时输出目录
        temp_output_dir = os.path.join(temp_dir, "output")
        os.makedirs(temp_output_dir, exist_ok=True)
        
        # 创建配置
        config = {
            "inputs": temp_file,
            "outputs": temp_output_dir,
            "visualize": visualize,
            "tasks": {
                "ocr": {
                    "model": "ocr_paddleocr",
                    "model_config": {
                        "use_angle_cls": use_angle_cls,
                        "lang": lang,
                        "det": det,
                        "rec": rec,
                        "cls": cls
                    }
                }
            }
        }
        
        # 初始化任务和模型
        task_instances = initialize_tasks_and_models(config)
        
        # 执行任务
        task = task_instances["ocr"]
        results = task.process(temp_file, save_dir=temp_output_dir, visualize=visualize)
        
        # 如果生成了可视化结果，则转换为Base64
        if visualize:
            # 查找可视化图像文件
            visualization_results = []
            for root, _, files in os.walk(temp_output_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)
                        base64_data = encode_image_to_base64(img_path)
                        visualization_results.append(base64_data)
            
            # 添加可视化结果到返回数据
            if results is None:
                results = {}
            results["visualizations"] = visualization_results
        
        return {
            "success": True,
            "message": "OCR任务完成",
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"OCR任务失败: {str(e)}",
            "results": None
        }
    finally:
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            cleanup_temp_dir(temp_dir)


@router.post("/formula-detection", response_model=TaskResponse)
async def formula_detection(
    file: UploadFile = File(...),
    img_size: int = Form(1024),
    conf_thres: float = Form(0.25),
    iou_thres: float = Form(0.45),
    visualize: bool = Form(False)
) -> Dict:
    """公式检测API。临时处理文件，不保存在服务器上。
    
    Args:
        file: 要上传的PDF或图像文件
        img_size: 图像大小
        conf_thres: 置信度阈值
        iou_thres: IOU阈值
        visualize: 是否可视化结果
    
    Returns:
        TaskResponse: 任务响应
    """
    temp_dir = None
    
    try:
        # 保存上传的文件到临时目录
        temp_dir, temp_file = await save_upload_file_temp(file)
        
        # 创建临时输出目录
        temp_output_dir = os.path.join(temp_dir, "output")
        os.makedirs(temp_output_dir, exist_ok=True)
        
        # 创建配置
        config = {
            "inputs": temp_file,
            "outputs": temp_output_dir,
            "tasks": {
                "formula_detection": {
                    "model": "formula_detection_yolo",
                    "model_config": {
                        "img_size": img_size,
                        "conf_thres": conf_thres,
                        "iou_thres": iou_thres,
                        "model_path": "models/FormDetect/yolo8m.pt",
                        "visualize": visualize
                    }
                }
            }
        }
        
        # 初始化任务和模型
        task_instances = initialize_tasks_and_models(config)
        
        # 执行任务
        model = task_instances["formula_detection"]
        model_results = model.predict_images(temp_file, temp_output_dir)
        
        # 获取id_to_names映射
        id_to_names = {
            0: 'inline',
            1: 'isolated'
        }
        
        # 将YOLO模型结果转换为可序列化格式
        results = []
        for res in model_results:
            if hasattr(res, '__dict__'):
                # 获取YOLO结果的boxes, classes, scores
                boxes = res.__dict__['boxes'].xyxy.tolist() if hasattr(res.__dict__['boxes'], 'xyxy') else []
                classes = res.__dict__['boxes'].cls.tolist() if hasattr(res.__dict__['boxes'], 'cls') else []
                scores = res.__dict__['boxes'].conf.tolist() if hasattr(res.__dict__['boxes'], 'conf') else []
                
                # 构建结构化的检测结果
                detections = []
                for i in range(len(boxes)):
                    if i < len(classes) and i < len(scores):
                        detections.append({
                            "box": boxes[i],
                            "class": int(classes[i]),
                            "class_name": id_to_names.get(int(classes[i]), "unknown"),
                            "score": float(scores[i])
                        })
                
                results.append({
                    "detections": detections
                })
            else:
                # 如果结果已经是字典格式，直接添加
                results.append(res)
        
        # 如果生成了可视化结果，则转换为Base64
        if visualize:
            # 查找可视化图像文件
            visualization_results = []
            for root, _, files in os.walk(temp_output_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)
                        base64_data = encode_image_to_base64(img_path)
                        visualization_results.append(base64_data)
            
            # 添加可视化结果到返回数据
            if results:
                results[0]["visualizations"] = visualization_results
            elif len(visualization_results) > 0:
                results = [{"visualizations": visualization_results}]
        
        return {
            "success": True,
            "message": "公式检测任务完成",
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"公式检测任务失败: {str(e)}",
            "results": None
        }
    finally:
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            cleanup_temp_dir(temp_dir)


@router.post("/formula-recognition", response_model=TaskResponse)
async def formula_recognition(
    file: UploadFile = File(...),
    beam_size: int = Form(5),
    max_seq_length: int = Form(400),
    visualize: bool = Form(False)
) -> Dict:
    """公式识别API。临时处理文件，不保存在服务器上。
    
    Args:
        file: 要上传的PDF或图像文件
        beam_size: 束搜索大小
        max_seq_length: 最大序列长度
        visualize: 是否可视化结果
    
    Returns:
        TaskResponse: 任务响应
    """
    temp_dir = None
    
    try:
        # 保存上传的文件到临时目录
        temp_dir, temp_file = await save_upload_file_temp(file)
        
        # 创建临时输出目录
        temp_output_dir = os.path.join(temp_dir, "output")
        os.makedirs(temp_output_dir, exist_ok=True)
        
        # 创建配置
        config = {
            "inputs": temp_file,
            "outputs": temp_output_dir,
            "tasks": {
                "formula_recognition": {
                    "model": "formula_recognition_nougat",
                    "model_config": {
                        "beam_size": beam_size,
                        "max_seq_length": max_seq_length
                    }
                }
            }
        }
        
        # 初始化任务和模型
        task_instances = initialize_tasks_and_models(config)
        
        # 执行任务
        model = task_instances["formula_recognition"]
        results = model.predict_images(temp_file, temp_output_dir)
        
        # 如果生成了可视化结果，则转换为Base64
        if visualize:
            # 查找可视化图像文件
            visualization_results = []
            for root, _, files in os.walk(temp_output_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)
                        base64_data = encode_image_to_base64(img_path)
                        visualization_results.append(base64_data)
            
            # 添加可视化结果到返回数据
            if results is None:
                results = {}
            results["visualizations"] = visualization_results
        
        return {
            "success": True,
            "message": "公式识别任务完成",
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"公式识别任务失败: {str(e)}",
            "results": None
        }
    finally:
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            cleanup_temp_dir(temp_dir)


@router.post("/table-parsing", response_model=TaskResponse)
async def table_parsing(
    file: UploadFile = File(...),
    visualize: bool = Form(False)
) -> Dict:
    """表格解析API。临时处理文件，不保存在服务器上。
    
    Args:
        file: 要上传的PDF或图像文件
        visualize: 是否可视化结果
    
    Returns:
        TaskResponse: 任务响应
    """
    temp_dir = None
    
    try:
        # 保存上传的文件到临时目录
        temp_dir, temp_file = await save_upload_file_temp(file)
        
        # 创建临时输出目录
        temp_output_dir = os.path.join(temp_dir, "output")
        os.makedirs(temp_output_dir, exist_ok=True)
        
        # 创建配置
        config = {
            "inputs": temp_file,
            "outputs": temp_output_dir,
            "tasks": {
                "table_parsing": {
                    "model": "table_parsing_tablestructuremodel",
                    "model_config": {
                        "structure_model_path": "models/CascadeTabNet/cascade_mask_rcnn_hrnetv2p_w32_20e.pth",
                        "cell_model_path": "models/CascadeTabNet/cell_cls_model.pth",
                        "visualize": visualize
                    }
                }
            }
        }
        
        # 初始化任务和模型
        task_instances = initialize_tasks_and_models(config)
        
        # 执行任务
        model = task_instances["table_parsing"]
        results = model.predict_images(temp_file, temp_output_dir)
        
        # 如果生成了可视化结果，则转换为Base64
        if visualize:
            # 查找可视化图像文件
            visualization_results = []
            for root, _, files in os.walk(temp_output_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)
                        base64_data = encode_image_to_base64(img_path)
                        visualization_results.append(base64_data)
            
            # 添加可视化结果到返回数据
            if results is None:
                results = {}
            results["visualizations"] = visualization_results
        
        return {
            "success": True,
            "message": "表格解析任务完成",
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"表格解析任务失败: {str(e)}",
            "results": None
        }
    finally:
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            cleanup_temp_dir(temp_dir)


@router.post("/pdf2markdown", response_model=TaskResponse)
async def pdf2markdown(
    file: UploadFile = File(...),
    merge2markdown: bool = Form(True)
) -> Dict:
    """PDF转Markdown API。临时处理文件，不保存在服务器上。
    
    Args:
        file: 要上传的PDF文件
        merge2markdown: 是否合并为Markdown
    
    Returns:
        TaskResponse: 任务响应
    """
    temp_dir = None
    
    try:
        # 保存上传的文件到临时目录
        temp_dir, temp_file = await save_upload_file_temp(file)
        
        # 创建临时输出目录
        temp_output_dir = os.path.join(temp_dir, "output")
        os.makedirs(temp_output_dir, exist_ok=True)
        
        # 创建配置
        config = {
            "inputs": temp_file,
            "outputs": temp_output_dir,
            "tasks": {
                "layout_detection": {
                    "model": "layout_detection_yolo",
                    "model_config": {
                        "model_path": "models/Layout/YOLO/doclayout_yolo_ft.pt",
                    }
                },
                "ocr": {
                    "model": "ocr_paddleocr",
                    "model_config": {
                        "use_angle_cls": True,
                        "lang": "ch"
                    }
                },
                "formula_detection": {
                    "model": "formula_detection_yolo",
                    "model_config": {
                        "model_path": "models/FormDetect/yolo8m.pt",
                    }
                },
                "formula_recognition": {
                    "model": "formula_recognition_nougat",
                    "model_config": {}
                }
            }
        }
        
        # 初始化任务和模型
        task_instances = initialize_tasks_and_models(config)
        
        # 执行布局检测
        layout_detection_task = task_instances["layout_detection"]
        layout_results = layout_detection_task.predict_images(temp_file, temp_output_dir)
        
        # 执行文字识别
        ocr_task = task_instances["ocr"]
        ocr_results = ocr_task.process(temp_file, save_dir=temp_output_dir)
        
        # 执行公式检测
        formula_detection_task = task_instances["formula_detection"]
        formula_detection_results = formula_detection_task.predict_images(temp_file, temp_output_dir)
        
        # 执行公式识别
        formula_recognition_task = task_instances["formula_recognition"]
        formula_recognition_results = formula_recognition_task.predict_images(temp_file, temp_output_dir)
        
        # 合并结果
        results = {
            "layout_detection": layout_results,
            "ocr": ocr_results,
            "formula_detection": formula_detection_results,
            "formula_recognition": formula_recognition_results
        }
        
        # 合并为Markdown
        if merge2markdown:
            # 这里假设有一个函数来合并结果为Markdown
            from pdf_extract_kit.utils.pdf2markdown import merge_to_markdown
            markdown_path = os.path.join(temp_output_dir, "output.md")
            markdown_content = merge_to_markdown(
                layout_results, 
                ocr_results, 
                formula_detection_results, 
                formula_recognition_results,
                save_path=markdown_path
            )
            
            # 读取Markdown内容
            with open(markdown_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()
            
            results["markdown"] = markdown_content
        
        return {
            "success": True,
            "message": "PDF转Markdown任务完成",
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"PDF转Markdown任务失败: {str(e)}",
            "results": None
        }
    finally:
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            cleanup_temp_dir(temp_dir)


@router.post("/run-project", response_model=TaskResponse)
async def run_project(
    file: UploadFile = File(...),
    config_content: str = Form("")
) -> Dict:
    """通过配置运行整个项目。临时处理文件，不保存在服务器上。
    
    Args:
        file: 要上传的PDF文件
        config_content: YAML格式的配置内容字符串
    
    Returns:
        TaskResponse: 任务响应
    """
    temp_dir = None
    
    try:
        # 保存上传的文件到临时目录
        temp_dir, temp_file = await save_upload_file_temp(file)
        
        # 创建临时输出目录
        temp_output_dir = os.path.join(temp_dir, "output")
        os.makedirs(temp_output_dir, exist_ok=True)
        
        # 如果提供了配置内容，则保存为临时配置文件
        if config_content:
            temp_config_path = os.path.join(temp_dir, "config.yaml")
            with open(temp_config_path, "w", encoding="utf-8") as f:
                f.write(config_content)
        else:
            # 使用默认配置
            config = {
                "inputs": temp_file,
                "outputs": temp_output_dir,
                "tasks": {
                    "layout_detection": {
                        "model": "layout_detection_yolo",
                        "model_config": {
                            "model_path": "models/Layout/YOLO/doclayout_yolo_ft.pt",
                        }
                    },
                    "ocr": {
                        "model": "ocr_paddleocr",
                        "model_config": {
                            "use_angle_cls": True,
                            "lang": "ch"
                        }
                    },
                    "formula_detection": {
                        "model": "formula_detection_yolo",
                        "model_config": {
                            "model_path": "models/FormDetect/yolo8m.pt",
                        }
                    },
                    "formula_recognition": {
                        "model": "formula_recognition_nougat",
                        "model_config": {}
                    }
                }
            }
            temp_config_path = os.path.join(temp_dir, "config.yaml")
            with open(temp_config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f)
        
        # 加载配置
        config = load_config(temp_config_path)
        
        # 修改输入和输出路径为临时路径
        config["inputs"] = temp_file
        config["outputs"] = temp_output_dir
        
        # 初始化任务和模型
        task_instances = initialize_tasks_and_models(config)
        
        # 执行任务并收集结果
        results = {}
        for task_name, task in task_instances.items():
            if hasattr(task, "predict_images"):
                task_results = task.predict_images(temp_file, temp_output_dir)
            elif hasattr(task, "process"):
                task_results = task.process(temp_file, save_dir=temp_output_dir)
            else:
                task_results = {"error": f"任务{task_name}没有可用的执行方法"}
            
            results[task_name] = task_results
        
        # 检查输出目录中的所有图像文件，并转换为Base64
        visualization_results = []
        for root, _, files in os.walk(temp_output_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(root, file)
                    base64_data = encode_image_to_base64(img_path)
                    visualization_results.append({"filename": file, "data": base64_data})
        
        # 添加可视化结果到返回数据
        results["visualizations"] = visualization_results
        
        # 收集所有文本文件内容
        text_results = []
        for root, _, files in os.walk(temp_output_dir):
            for file in files:
                if file.lower().endswith(('.txt', '.md', '.json')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        text_results.append({"filename": file, "content": content})
                    except Exception as e:
                        text_results.append({"filename": file, "error": str(e)})
        
        # 添加文本文件内容到返回数据
        results["text_files"] = text_results
        
        return {
            "success": True,
            "message": "项目运行完成",
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"项目运行失败: {str(e)}",
            "results": None
        }
    finally:
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            cleanup_temp_dir(temp_dir)


@router.post("/pdf-to-images", response_model=TaskResponse)
async def pdf_to_images(
    file: UploadFile = File(...),
    dpi: int = Form(200),
    output_format: str = Form("png")
) -> Dict:
    """将PDF转换为图像API。
    
    Args:
        file: 要上传的PDF文件
        dpi: 图像DPI
        output_format: 输出图像格式(png或jpg)
    
    Returns:
        TaskResponse: 任务响应，包含生成的图像信息
    """
    temp_dir = None
    
    try:
        # 检查文件扩展名是否为PDF
        if not file.filename.lower().endswith(".pdf"):
            return {
                "success": False,
                "message": "只接受PDF文件",
                "results": None
            }
        
        # 保存上传的文件到临时目录
        temp_dir, temp_file = await save_upload_file_temp(file)
        
        # 创建临时输出目录
        temp_output_dir = os.path.join(temp_dir, "output")
        os.makedirs(temp_output_dir, exist_ok=True)
        
        # 检查输出格式是否有效
        if output_format.lower() not in ["png", "jpg", "jpeg"]:
            output_format = "png"
        
        # 将PDF转换为图像
        image_paths = convert_pdf_to_images(
            pdf_path=temp_file,
            output_dir=temp_output_dir,
            dpi=dpi,
            output_format=output_format
        )
        
        # 将图像转换为Base64
        images_base64 = []
        for image_path in image_paths:
            base64_data = encode_image_to_base64(image_path)
            images_base64.append({
                "filename": os.path.basename(image_path),
                "format": base64_data["format"],
                "data": base64_data["data"]
            })
        
        return {
            "success": True,
            "message": f"PDF已成功转换为{len(image_paths)}张图像",
            "results": {
                "page_count": len(image_paths),
                "images": images_base64
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"PDF转图像任务失败: {str(e)}",
            "results": None
        }
    finally:
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            cleanup_temp_dir(temp_dir)


@router.post("/pdf-to-images-save", response_model=TaskResponse)
async def pdf_to_images_save(
    file: UploadFile = File(...),
    dpi: int = Form(200),
    output_format: str = Form("png")
) -> Dict:
    """将PDF转换为图像API（持久化版本）。图像保存在服务器上，不返回Base64数据。
    
    Args:
        file: 要上传的PDF文件
        dpi: 图像DPI
        output_format: 输出图像格式(png或jpg)
    
    Returns:
        TaskResponse: 任务响应，包含保存的图像文件路径
    """
    try:
        # 检查文件扩展名是否为PDF
        if not file.filename.lower().endswith(".pdf"):
            return {
                "success": False,
                "message": "只接受PDF文件",
                "results": None
            }
        
        # 为上传的文件创建唯一ID
        task_id = str(uuid.uuid4())
        
        # 准备上传目录和输出目录
        upload_dir = ensure_data_dir(f"data/uploads/{task_id}")
        output_dir = ensure_data_dir(f"data/outputs/pdf_to_images/{task_id}")
        
        # 保存上传的PDF文件
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 检查输出格式是否有效
        if output_format.lower() not in ["png", "jpg", "jpeg"]:
            output_format = "png"
        
        # 将PDF转换为图像
        image_paths = convert_pdf_to_images(
            pdf_path=file_path,
            output_dir=output_dir,
            dpi=dpi,
            output_format=output_format
        )
        
        # 准备返回结果
        relative_paths = [os.path.relpath(path, ROOT_DIR) for path in image_paths]
        
        return {
            "success": True,
            "message": f"PDF已成功转换为{len(image_paths)}张图像",
            "results": {
                "page_count": len(image_paths),
                "image_paths": relative_paths,
                "output_dir": os.path.relpath(output_dir, ROOT_DIR)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"PDF转图像任务失败: {str(e)}",
            "results": None
        }