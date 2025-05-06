from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field
from fastapi import UploadFile


class TaskRequest(BaseModel):
    """任务请求基础模型。
    
    Args:
        output_dir: 输出目录路径(可选)
        visualize: 是否可视化结果(可选)
    """
    output_dir: Optional[str] = None
    visualize: bool = False


class FileTaskRequest(TaskRequest):
    """基于文件的任务请求模型。
    
    Args:
        file: 上传的文件
    """
    file: UploadFile


class LayoutDetectionRequest(TaskRequest):
    """布局检测请求模型。
    
    Args:
        img_size: 图像大小
        conf_thres: 置信度阈值
        iou_thres: IOU阈值
        model_path: 模型路径
    """
    img_size: int = 1024
    conf_thres: float = 0.25
    iou_thres: float = 0.45
    model_path: Optional[str] = None


class OCRRequest(TaskRequest):
    """OCR请求模型。
    
    Args:
        use_angle_cls: 是否使用角度分类
        lang: 语言
        det: 是否进行检测
        rec: 是否进行识别
        cls: 是否进行分类
    """
    use_angle_cls: bool = True
    lang: str = "ch"
    det: bool = True
    rec: bool = True
    cls: bool = True


class FormulaDetectionRequest(TaskRequest):
    """公式检测请求模型。
    
    Args:
        img_size: 图像大小
        conf_thres: 置信度阈值
        iou_thres: IOU阈值
        model_path: 模型路径
    """
    img_size: int = 1024
    conf_thres: float = 0.25
    iou_thres: float = 0.45
    model_path: Optional[str] = None


class FormulaRecognitionRequest(TaskRequest):
    """公式识别请求模型。
    
    Args:
        beam_size: 束搜索大小
        max_seq_length: 最大序列长度
    """
    beam_size: int = 5
    max_seq_length: int = 400


class TableParsingRequest(TaskRequest):
    """表格解析请求模型。
    
    Args:
        structure_model_path: 结构模型路径
        cell_model_path: 单元格模型路径
    """
    structure_model_path: Optional[str] = None
    cell_model_path: Optional[str] = None


class PDF2MarkdownRequest(TaskRequest):
    """PDF转Markdown请求模型。
    
    Args:
        merge2markdown: 是否合并为Markdown
        layout_model_path: 布局检测模型路径
        mfd_model_path: 公式检测模型路径
        mfr_model_path: 公式识别模型路径
        ocr_model_path: OCR模型路径
    """
    merge2markdown: bool = True
    layout_model_path: Optional[str] = None
    mfd_model_path: Optional[str] = None
    mfr_model_path: Optional[str] = None
    ocr_model_path: Optional[str] = None


class RunProjectRequest(BaseModel):
    """运行项目请求模型。
    
    Args:
        config_path: 配置文件路径
    """
    config_path: str


class PDFToImagesRequest(TaskRequest):
    """PDF转图片请求模型。
    
    Args:
        dpi: 图像DPI(可选)
        output_format: 输出图像格式(可选)
    """
    dpi: int = 200
    output_format: str = "png"


class TaskResponse(BaseModel):
    """任务响应模型。
    
    Args:
        success: 是否成功
        message: 消息
        results: 结果数据(可选)
    """
    success: bool
    message: str
    results: Optional[Union[List, Dict, Any]] = None


class Base64Image(BaseModel):
    """Base64编码的图像。
    
    Args:
        format: 图像格式
        data: Base64编码的图像数据
    """
    format: str
    data: str 