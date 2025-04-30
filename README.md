# 中国国家公园图片采集系统

这是一个自动化图片采集系统，专门用于获取中国国家公园的代表性图片。该系统从百度图片搜索中获取每个国家公园的特色图片，并按照结构化的方式保存。

## 功能特点

- 自动读取国家公园数据文件
- **可配置**下载图片数量 (`src/config.py`)
- **可配置**图片保存目录 (`src/config.py`)
- **可配置**数据文件路径 (`src/config.py`)
- **可配置**关键词生成逻辑 (`src/config.py`)
- **可配置**最低分辨率和宽高比范围 (应用于下载的缩略图) (`src/config.py`)
- 自动去重 (基于图片内容哈希)，确保图片唯一性
- 按照国家公园名称分类存储图片
- 自动化批量处理所有国家公园
- 自动翻页查找，直到找到足够数量的合格图片 (最多检查5页)

## 项目结构

```
internet_data_scrapper/
│
├── data/                      # 数据文件目录
│   └── 中国国家公园名册.csv    # 国家公园基础数据
│
├── src/                       # 源代码目录
│   ├── config.py              # 配置文件
│   └── baidu_scrapper_valid.py  # 百度图片爬虫核心模块
│
├── images/                    # 图片保存目录（路径可配置）
│   ├── 三江源国家公园/         # 各国家公园图片子目录
│   ├── 东北虎豹国家公园/
│   └── ...
│
├── main.py                    # 主程序入口
└── README.md                  # 项目说明文档
```

## 环境要求

- Python 3.6+
- 依赖包：
  - pandas：用于读取CSV文件
  - requests：用于网络请求
  - Pillow：用于图片尺寸和格式处理 (⭐新增⭐)

## 安装步骤

1. 克隆或下载本项目
2. 安装所需依赖：
```bash
pip install pandas requests Pillow
```

## 配置

在 `src/config.py` 文件中，你可以调整以下参数：

- `IMAGES_PER_PARK`: 每个公园下载的图片数量
- `IMAGES_BASE_DIR`: 图片保存的基础目录
- `DATA_FILE_PATH`: 国家公园CSV数据文件的路径
- `REQUEST_TIMEOUT`: 网络请求超时时间（秒）
- `BAIDU_RESULTS_PER_PAGE`: 百度每页返回结果数
- `HEADERS`: 请求头信息
- `LANDSCAPE_FEATURES`: 用于提取关键词的特征列表
- `DEFAULT_KEYWORD_SUFFIX`: 默认关键词后缀
- `MAX_FEATURES_IN_KEYWORD`: 关键词中包含的最大特征数
- `MIN_RESOLUTION`: (⭐新增⭐) 图片最低分辨率 `(宽, 高)`，设为 `None` 或 `(0, 0)` 则禁用。
- `ASPECT_RATIO_RANGE`: (⭐新增⭐) 允许的宽高比范围 `(最小比, 最大比)`，设为 `None` 则禁用。

*注意：* 分辨率和宽高比检查目前应用于百度返回的缩略图 (`thumbURL`)。

## 使用方法

1. （可选）根据需要修改 `src/config.py` 中的配置
2. 确保数据文件存在于 `config.py` 指定的路径
3. 运行主程序：
```bash
python main.py
```
4. 程序会自动在配置的 `IMAGES_BASE_DIR` 目录下创建子目录并下载符合要求的图片

## 输出说明

- 每个国家公园的图片都保存在其专属文件夹中
- 图片按照 `000000.jpg`, `000001.jpg`, ... 格式命名
- 程序运行过程中会显示下载进度、使用的搜索关键词以及因尺寸/比例/重复而被跳过的图片信息

## 代码结构说明

### main.py
- 程序的主入口点
- 从 `config` 加载基础目录
- 调用 `get_national_parks` 获取公园信息
- 遍历公园列表，调用 `download_park_images`

### src/baidu_scrapper_valid.py
- 从 `config` 加载各种参数
- `get_national_parks()`: 读取公园数据
- `extract_key_features()`, `generate_search_keyword()`: 生成搜索关键词
- `is_image_valid()`: (⭐新增⭐) 检查图片尺寸和宽高比
- `get_images_from_baidu()`: 实现百度图片搜索、下载、验证（尺寸、比例、哈希）和去重逻辑，包含自动翻页
- `download_park_images()`: 处理单个公园的图片下载流程

### src/config.py
- 集中管理所有可配置参数

## 注意事项

- 请确保网络连接稳定
- 下载的图片仅供学习研究使用
- 建议在使用时遵守相关网站的使用条款和规范
- 分辨率和宽高比筛选目前基于缩略图，可能与原图有差异。

## 维护与更新

本项目仍在持续维护中。如有问题或建议，欢迎提出。 