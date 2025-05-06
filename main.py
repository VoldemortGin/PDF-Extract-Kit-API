import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from dotenv import load_dotenv
import distutils.util

import rootutils

ROOT_DIR = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

load_dotenv(ROOT_DIR / ".env")

# 获取IS_PROD环境变量，默认为False
IS_PROD = bool(distutils.util.strtobool(os.getenv("IS_PROD", "False")))

from src.api.routes import router
from src.api.router_upload import router as upload_router
from src.api.utils import setup_logging

# 配置日志
logger = setup_logging()
logger.info(f"运行模式: {'生产环境' if IS_PROD else '开发环境'}")

# 创建FastAPI应用
app = FastAPI(
    title="PDF-Extract-Kit API",
    description="PDF数据提取工具箱API，提供布局检测、OCR、公式检测与识别、表格解析等功能。临时处理文件，不进行持久化存储。",
    version="1.0.0",
    docs_url=None,  # 禁用默认的docs URL
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义Swagger UI页面。
    
    Returns:
        HTMLResponse: Swagger UI HTML页面
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.0.0/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.0.0/swagger-ui.css",
    )


@app.get("/")
async def root():
    """API根路径。
    
    Returns:
        dict: 包含API基本信息的响应
    """
    return {
        "message": "欢迎使用PDF-Extract-Kit API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """健康检查端点。
    
    Returns:
        dict: 包含服务健康状态的响应
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    # 启动服务，根据IS_PROD决定reload参数
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=not IS_PROD,  # 非生产环境启用热重载
        log_level="info",
    ) 