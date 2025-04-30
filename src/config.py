"""
Configuration settings for the Baidu Image Scraper.
"""

import os

# --- Image Download Settings ---
IMAGES_PER_PARK = 3  # Number of unique images to download per park
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
DEFAULT_KEYWORD_SUFFIX = '风景 标志性' # Default suffix if no features are extracted
MAX_FEATURES_IN_KEYWORD = 2 # Max number of features to include in the search keyword

# --- Image Filtering Settings (Applied to downloaded thumbnails) ---
# Set MIN_RESOLUTION to None or (0, 0) to disable resolution check
MIN_RESOLUTION = (800, 800)  # Minimum required resolution (width, height) in pixels. 
# Set ASPECT_RATIO_RANGE to None to disable aspect ratio check
# Example ranges:
# (1.0, 1.0) for square images
# (1.5, 1.8) for landscape (e.g., 16:9 is 1.77)
# (0.6, 0.8) for portrait (e.g., 9:16 is 0.56)
ASPECT_RATIO_RANGE = (1.2, 2.0) # Allowed aspect ratio range (width / height). Set to a wide range by default.

# --- Advanced Settings (Informational) ---
# Filtering based on full resolution images would require fetching objURL and parsing HTML/image data,
# which is more complex than the current thumbURL approach.
# TARGET_RESOLUTION = (1920, 1080)
# TARGET_ASPECT_RATIO = 16 / 9 