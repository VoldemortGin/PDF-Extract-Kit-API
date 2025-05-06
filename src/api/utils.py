import os
import logging
import tempfile
import shutil
import base64
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
import uuid
from fastapi import UploadFile


def ensure_data_dir(directory: str) -> str:
    """确保目录存在，如果不存在则创建。
    
    Args:
        directory: 需要确保存在的目录路径
    
    Returns:
        str: 已确保存在的目录路径
    
    Example:
        >>> ensure_data_dir("data/outputs/ocr")
        'data/outputs/ocr'
    """
    # 确保所有输出目录都在data/下
    if not directory.startswith("data/"):
        directory = os.path.join("data", directory)
    
    # 创建目录
    os.makedirs(directory, exist_ok=True)
    return directory


def setup_logging(log_file: str = "data/logs/api.log", level: int = logging.INFO) -> logging.Logger:
    """设置日志记录器。
    
    Args:
        log_file: 日志文件路径
        level: 日志级别
    
    Returns:
        logging.Logger: 配置好的日志记录器
    
    Example:
        >>> logger = setup_logging()
        >>> logger.info("这是一条信息日志")
    """
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    ensure_data_dir(log_dir)
    
    # 配置日志记录器
    logger = logging.getLogger("pdf_extract_kit_api")
    logger.setLevel(level)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


async def save_upload_file_temp(upload_file: UploadFile) -> Tuple[str, str]:
    """将上传的文件保存到临时目录。
    
    Args:
        upload_file: 上传的文件
    
    Returns:
        Tuple[str, str]: 临时目录路径和临时文件路径
    
    Example:
        >>> temp_dir, temp_file = await save_upload_file_temp(upload_file)
    """
    temp_dir = tempfile.mkdtemp()
    
    temp_file = os.path.join(temp_dir, upload_file.filename)
    
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    await upload_file.seek(0)
    
    return temp_dir, temp_file


def encode_image_to_base64(image_path: str) -> Dict[str, str]:
    """将图像编码为Base64格式。
    
    Args:
        image_path: 图像文件路径
    
    Returns:
        Dict[str, str]: 包含格式和Base64数据的字典
    
    Example:
        >>> encode_image_to_base64("path/to/image.jpg")
        {'format': 'jpg', 'data': 'base64_encoded_string'}
    """
    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
    
    file_ext = os.path.splitext(image_path)[1].lstrip(".")
    
    return {
        "format": file_ext,
        "data": encoded_string
    }


def cleanup_temp_dir(temp_dir: str) -> None:
    """清理临时目录。
    
    Args:
        temp_dir: 临时目录路径
    
    Returns:
        None
    
    Example:
        >>> cleanup_temp_dir("/tmp/tmpdir12345")
    """
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        logging.error(f"清理临时目录失败: {e}")


def convert_pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 200, output_format: str = "png") -> List[str]:
    """将PDF文件转换为图像。
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录路径
        dpi: 图像DPI
        output_format: 输出图像格式
    
    Returns:
        List[str]: 生成的图像文件路径列表
    
    Example:
        >>> convert_pdf_to_images("path/to/file.pdf", "path/to/output", dpi=300, output_format="jpg")
        ['path/to/output/page_1.jpg', 'path/to/output/page_2.jpg']
    """
    from pdf2image import convert_from_path
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 转换PDF为图像
    images = convert_from_path(pdf_path, dpi=dpi)
    
    # 保存图像
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"page_{i+1}.{output_format}")
        image.save(image_path, output_format.upper())
        image_paths.append(image_path)
    
    return image_paths 