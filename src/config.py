"""
Configuration settings for the Baidu Image Scraper.
"""

import os

# --- Image Download Settings ---
IMAGES_PER_SEASON = 1  # Number of unique images to download per season per park
IMAGES_PER_COVER = 1   # Number of cover photos to download per park
IMAGES_BASE_DIR = '.\\images'  # Base directory to save images

# --- Data Source Settings ---
DATA_FILE_PATH = 'data/中国国家公园名册.csv'  # Path to the national parks data file

# --- Request Settings ---
REQUEST_TIMEOUT = 10  # Timeout for network requests in seconds
BAIDU_RESULTS_PER_PAGE = 30  # Number of results Baidu returns per page (rn parameter)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}

# --- Keyword Generation Settings ---
LANDSCAPE_FEATURES = [
    '冰川', '雪山', '江源', '河流', '湖泊', '湿地', '草甸', '热带雨林', 
    '森林', '山脉', '峰', '溪', '草原', '峡谷'
]  # Keywords used to extract features from description

SEASONS = {
    '春': ['春天', '春季', '春日'],
    '夏': ['夏天', '夏季', '盛夏'],
    '秋': ['秋天', '秋季', '金秋'],
    '冬': ['冬天', '冬季', '寒冬']
}  # Seasons and their alternative expressions

# 封面图片的关键词后缀选项，用于生成更丰富的搜索关键词
COVER_KEYWORD_SUFFIXES = [
    '标志性景观',
    '地标景观',
    '震撼全景',
]

DEFAULT_KEYWORD_SUFFIX = '风景 实拍' # Default suffix if no features are extracted
MAX_FEATURES_IN_KEYWORD = 2 # Max number of features to include in the search keyword

# --- Image Filtering Settings ---
# 季节图片的过滤设置
# Set MIN_RESOLUTION to None or (0, 0) to disable resolution check
SEASON_MIN_RESOLUTION = (500, 500)  # Minimum required resolution (width, height) in pixels
# Set ASPECT_RATIO_RANGE to None to disable aspect ratio check
# Example ranges:
# (1.0, 1.0) for square images
# (1.5, 1.8) for landscape (e.g., 16:9 is 1.77)
# (0.6, 0.8) for portrait (e.g., 9:16 is 0.56)
SEASON_ASPECT_RATIO_RANGE = (0.5, 2.0)  # Allowed aspect ratio range (width / height)

# 封面图片的过滤设置（更高的质量要求）
COVER_MIN_RESOLUTION = (800, 800)  # 封面图片最小分辨率要求（全高清）
COVER_ASPECT_RATIO_RANGE = (1.5, 2.1)  # 封面图片宽高比范围，偏好宽幅全景图
# 1.6-2.1的宽高比大致对应于：
# - 16:9 = 1.77 (标准宽屏)
# - 16:10 = 1.6 (宽屏)
# - 21:9 = 2.33 (超宽屏，但我们设为2.1作为上限以避免过于极端)

# --- Image Similarity Settings ---
# 感知哈希(pHash)相似度阈值设置
# 值越小要求越严格，图片差异需要更小才能通过
# 推荐范围：5-15
# 5: 要求非常相似才会被认为是重复（可能导致有些相似图片无法被过滤）
# 10: 中等严格度，可以检测出明显相似的图片
# 15: 宽松的判断标准，可以检测出较为相似的图片
PHASH_THRESHOLD = 15

# 是否启用图片尺寸检查
# 如果为True，则完全相同尺寸的图片会被认为是重复的
# 如果为False，则不会使用尺寸作为判断依据
CHECK_IMAGE_SIZE = False

# 是否启用MD5完全匹配
# 如果为True，则完全相同的图片（按字节比较）会被认为是重复的
# 如果为False，则只使用感知哈希进行相似度判断
CHECK_MD5_HASH = True

# --- Advanced Settings (Informational) ---
# Filtering based on full resolution images would require fetching objURL and parsing HTML/image data,
# which is more complex than the current thumbURL approach.
# TARGET_RESOLUTION = (1920, 1080)
# TARGET_ASPECT_RATIO = 16 / 9 