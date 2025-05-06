import os
import uuid
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import base64

import rootutils

ROOT_DIR = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from src.api.utils import save_upload_file_temp, encode_image_to_base64, cleanup_temp_dir

router = APIRouter()


class UploadResponse(BaseModel):
    """上传响应模型。
    
    Args:
        success: 是否成功
        message: 消息
        file_data: 文件Base64编码数据
        file_name: 文件名
        file_type: 文件类型
    """
    success: bool
    message: str
    file_data: str
    file_name: str
    file_type: str


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """文件上传API，用于上传PDF文件或图像。不会持久化存储文件，处理后返回Base64编码。
    
    Args:
        file: 要上传的文件
    
    Returns:
        UploadResponse: 上传结果响应
    
    Raises:
        HTTPException: 如果上传过程中出现错误
    """
    try:
        # 获取文件扩展名
        _, ext = os.path.splitext(file.filename)
        
        # 检查文件类型是否为PDF或图像
        allowed_extensions = [".pdf", ".jpg", ".jpeg", ".png", ".tif", ".tiff"]
        if ext.lower() not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {ext}。只允许PDF或图像文件。"
            )
        
        # 保存到临时文件
        temp_dir, temp_file = await save_upload_file_temp(file)
        
        try:
            # 将文件转换为Base64
            file_content = ""
            with open(temp_file, "rb") as f:
                file_content = base64.b64encode(f.read()).decode("utf-8")
            
            return {
                "success": True,
                "message": "文件上传成功",
                "file_data": file_content,
                "file_name": file.filename,
                "file_type": ext.lower().lstrip(".")
            }
        finally:
            # 清理临时文件
            cleanup_temp_dir(temp_dir)
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
    finally:
        # 确保关闭文件
        await file.close() 