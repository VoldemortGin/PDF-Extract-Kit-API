# PDF-Extract-Kit API 测试说明

本目录包含 PDF-Extract-Kit API 的测试代码，用于验证API服务的各项功能是否正常工作。

## 测试内容

测试覆盖了以下API端点：

1. **基础端点**
   - `/` - 根路径
   - `/health` - 健康检查

2. **文件上传**
   - `/api/v1/upload` - 文件上传API

3. **PDF处理API**
   - `/api/v1/layout-detection` - 布局检测API
   - `/api/v1/ocr` - OCR文字识别API
   - `/api/v1/formula-detection` - 公式检测API
   - `/api/v1/formula-recognition` - 公式识别API
   - `/api/v1/table-parsing` - 表格解析API
   - `/api/v1/pdf2markdown` - PDF转Markdown API
   - `/api/v1/run-project` - 通过配置运行项目API
   - `/api/v1/pdf-to-images` - PDF转图像API
   - `/api/v1/pdf-to-images-save` - PDF转图像并保存API

## 测试文件组织

- `conftest.py` - 包含共享的pytest夹具(fixtures)
- `test_api_endpoints.py` - 主要API端点测试
- `test_upload.py` - 文件上传功能的专项测试
- `test_pdf_to_images.py` - PDF转图像功能的专项测试

## 测试夹具(Fixtures)

我们提供了以下pytest夹具，用于简化测试代码：

1. `client` - FastAPI测试客户端
2. `test_files` - 测试用PDF和图像文件
3. `temp_directory` - 临时目录
4. `temp_text_file` - 临时文本文件

## 运行测试

### 运行全部测试

```bash
# 在项目根目录下执行
pytest tests/ -v
```

### 运行特定的测试文件

```bash
# 运行API端点测试
pytest tests/test_api_endpoints.py -v

# 运行上传功能测试
pytest tests/test_upload.py -v

# 运行PDF转图像功能测试
pytest tests/test_pdf_to_images.py -v
```

### 运行特定的测试函数

```bash
# 运行特定的测试函数
pytest tests/test_api_endpoints.py::test_pdf2markdown -v
```

## 测试准备

测试会自动创建所需的测试文件，存放在 `data/test_files/` 目录下：

- `sample.pdf` - 测试用PDF文件
- `sample.png` - 测试用图像文件

这些文件会在首次运行测试时自动创建，之后会重复使用这些文件以提高测试效率。

## 注意事项

1. 测试会使用临时目录和临时文件，结束后会自动清理。
2. 测试依赖于配置正确的环境和模型文件的存在。
3. 确保已经安装了所有必要的依赖包：

```bash
uv pip install -r requirements.txt
uv pip install pytest pytest-cov
```

## 生成测试覆盖率报告

```bash
# 生成HTML覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

生成的报告会保存在 `htmlcov/` 目录下，可以在浏览器中打开 `htmlcov/index.html` 查看测试覆盖率详情。 