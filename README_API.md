# PDF-Extract-Kit API

PDF-Extract-Kit API 是一个基于 FastAPI 的 HTTP 服务，用于暴露 PDF-Extract-Kit 工具箱的功能。

## 功能特点

- 布局检测：检测文档页面中的布局元素
- OCR：光学字符识别
- 公式检测：检测文档中的数学公式区域
- 公式识别：识别数学公式并转换为 LaTeX
- 表格解析：解析文档中的表格结构

## 安装与运行

### 安装依赖

```bash
# 使用 uv 安装依赖
uv pip install -r requirements.txt
uv pip install -r requirements-api.txt
```

### 运行 API 服务

```bash
python main.py
```

服务默认运行在 `http://localhost:8000`，API 文档可在 `http://localhost:8000/docs` 访问。

## API 端点

### 文件上传

- **POST** `/api/v1/upload`
  - 描述：上传 PDF 文件或图像
  - 请求：`multipart/form-data` 格式，文件字段名为 `files`
  - 响应：上传的文件路径列表

### 布局检测

- **POST** `/api/v1/layout-detection`
  - 描述：检测文档页面中的布局元素
  - 请求参数：
    - `input_data`: 输入数据路径
    - `output_dir`: 输出目录（可选）
    - `visualize`: 是否可视化结果
    - `img_size`: 图像大小
    - `conf_thres`: 置信度阈值
    - `iou_thres`: IOU阈值
    - `model_path`: 模型路径（可选）

### OCR

- **POST** `/api/v1/ocr`
  - 描述：对文档进行光学字符识别
  - 请求参数：
    - `input_data`: 输入数据路径
    - `output_dir`: 输出目录（可选）
    - `visualize`: 是否可视化结果
    - `use_angle_cls`: 是否使用角度分类
    - `lang`: 语言
    - `det`: 是否进行检测
    - `rec`: 是否进行识别
    - `cls`: 是否进行分类

### 公式检测

- **POST** `/api/v1/formula-detection`
  - 描述：检测文档中的数学公式区域
  - 请求参数：
    - `input_data`: 输入数据路径
    - `output_dir`: 输出目录（可选）
    - `visualize`: 是否可视化结果
    - `img_size`: 图像大小
    - `conf_thres`: 置信度阈值
    - `iou_thres`: IOU阈值
    - `model_path`: 模型路径（可选）

### 公式识别

- **POST** `/api/v1/formula-recognition`
  - 描述：识别数学公式并转换为 LaTeX
  - 请求参数：
    - `input_data`: 输入数据路径
    - `output_dir`: 输出目录（可选）
    - `visualize`: 是否可视化结果
    - `beam_size`: 束搜索大小
    - `max_seq_length`: 最大序列长度

### 表格解析

- **POST** `/api/v1/table-parsing`
  - 描述：解析文档中的表格结构
  - 请求参数：
    - `input_data`: 输入数据路径
    - `output_dir`: 输出目录（可选）
    - `visualize`: 是否可视化结果
    - `structure_model_path`: 结构模型路径（可选）
    - `cell_model_path`: 单元格模型路径（可选）

## 示例

### 上传文件

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@sample.pdf'
```

### 执行布局检测

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/layout-detection' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "input_data": "path/to/uploaded/file.pdf",
    "visualize": true
  }'
```

## 数据存储

所有数据都存储在 `data/` 目录下：

- `data/uploads/`: 上传的文件
- `data/outputs/`: 任务输出结果
- `data/logs/`: 日志文件
- `data/static/`: 静态文件（可通过 /static 路径访问） 