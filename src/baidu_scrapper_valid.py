# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 10:17:50 2023
@author: MatpyMaster
"""

"""
Baidu Image Scraper Module

This module provides functionality to scrape images from Baidu Image Search.
It includes functions to download images for given keywords and to get national park names from a CSV file.
"""

import requests
import os
import re
import pandas as pd
import hashlib
import random
# Add imports for image processing
from io import BytesIO
from PIL import Image
from .config import (
    IMAGES_PER_SEASON,
    IMAGES_PER_COVER,
    DATA_FILE_PATH,
    REQUEST_TIMEOUT,
    BAIDU_RESULTS_PER_PAGE,
    HEADERS,
    LANDSCAPE_FEATURES,
    DEFAULT_KEYWORD_SUFFIX,
    MAX_FEATURES_IN_KEYWORD,
    SEASONS,
    COVER_KEYWORD_SUFFIXES,
    # Import image filtering settings
    SEASON_MIN_RESOLUTION,
    SEASON_ASPECT_RATIO_RANGE,
    COVER_MIN_RESOLUTION,
    COVER_ASPECT_RATIO_RANGE,
    # Import similarity settings
    PHASH_THRESHOLD,
    CHECK_IMAGE_SIZE,
    CHECK_MD5_HASH
)

def extract_key_features(description):
    """
    从公园描述中提取关键特征
    """
    features = []
    # Use features defined in config
    for feature in LANDSCAPE_FEATURES:
        if feature in description:
            features.append(feature)
    return features

def generate_search_keyword(park_name, description, season):
    """
    生成优化的搜索关键词，包含季节信息
    
    Args:
        park_name (str): 公园名称
        description (str): 公园描述
        season (str): 季节 ('春', '夏', '秋', '冬')
    """
    features = extract_key_features(description)
    if features:
        # Use max features defined in config
        features = features[:MAX_FEATURES_IN_KEYWORD]
        search_keyword = f"{park_name} {season}季 风景 {' '.join(features)}"
    else:
        # Use default suffix from config
        search_keyword = f"{park_name} {season}季 {DEFAULT_KEYWORD_SUFFIX}"
    return search_keyword

def generate_cover_search_keyword(park_name, description):
    """
    生成封面图片的优化搜索关键词
    
    Args:
        park_name (str): 公园名称
        description (str): 公园描述
    """
    features = extract_key_features(description)
    # 随机选择一个封面关键词后缀
    cover_suffix = random.choice(COVER_KEYWORD_SUFFIXES)
    
    if features:
        # Use max features defined in config
        features = features[:MAX_FEATURES_IN_KEYWORD]
        search_keyword = f"{park_name} {' '.join(features)} {cover_suffix}"
    else:
        # Use cover suffix
        search_keyword = f"{park_name} {cover_suffix}"
    return search_keyword

def get_national_parks():
    """
    从CSV文件读取国家公园信息，并返回完整的DataFrame以及公园信息列表
    
    Returns:
        tuple: (DataFrame, list of dicts) DataFrame是完整的CSV数据，list包含所需的公园信息
    """
    # Use data file path from config
    df = pd.read_csv(DATA_FILE_PATH)
    
    # 确保新的图片URL列存在
    for col in ['封面图', '春图', '夏图', '秋图', '冬图']:
        if col not in df.columns:
            df[col] = ''
    
    # 保存更新后的CSV（如果有新列的话）
    df.to_csv(DATA_FILE_PATH, index=False)
    
    # 返回DataFrame和公园信息列表
    parks_info = [{'name': row['名称'], 'description': row['描述']} for _, row in df.iterrows()]
    return df, parks_info

def update_park_image_url(park_name, season, image_url):
    """
    更新CSV文件中特定公园的图片URL
    
    Args:
        park_name (str): 公园名称
        season (str): 季节或'封面'
        image_url (str): 图片URL
    """
    try:
        df = pd.read_csv(DATA_FILE_PATH)
        
        # 确定要更新的列名
        column_map = {
            '春': '春图',
            '夏': '夏图',
            '秋': '秋图',
            '冬': '冬图',
            'cover': '封面图'
        }
        
        column = column_map.get(season)
        if not column:
            print(f"Warning: Unknown season/type '{season}'")
            return
            
        # 更新特定公园的图片URL
        df.loc[df['名称'] == park_name, column] = image_url
        
        # 保存更新后的CSV
        df.to_csv(DATA_FILE_PATH, index=False)
        print(f"Updated {column} URL for {park_name}")
        
    except Exception as e:
        print(f"Error updating CSV file: {e}")

def is_image_valid(image_data, is_cover=False):
    """
    检查图片是否满足分辨率和宽高比要求
    
    Args:
        image_data (bytes): 图片二进制数据
        is_cover (bool): 是否是封面图片
    """
    try:
        img = Image.open(BytesIO(image_data))
        width, height = img.size

        # 根据图片类型选择对应的配置
        min_resolution = COVER_MIN_RESOLUTION if is_cover else SEASON_MIN_RESOLUTION
        aspect_ratio_range = COVER_ASPECT_RATIO_RANGE if is_cover else SEASON_ASPECT_RATIO_RANGE

        # 1. Resolution Check
        if min_resolution and min_resolution != (0, 0):
            if width < min_resolution[0] or height < min_resolution[1]:
                print(f"Skipping image: Resolution ({width}x{height}) below minimum {min_resolution}")
                return False

        # 2. Aspect Ratio Check
        if aspect_ratio_range:
            if height == 0: # Avoid division by zero
                print("Skipping image: Height is 0")
                return False 
            aspect_ratio = width / height
            min_ratio, max_ratio = aspect_ratio_range
            if not (min_ratio <= aspect_ratio <= max_ratio):
                print(f"Skipping image: Aspect ratio ({aspect_ratio:.2f}) outside range [{min_ratio}-{max_ratio}]")
                return False
                
        return True # All checks passed

    except Exception as e:
        print(f"Error validating image: {e}")
        return False # Treat validation errors as invalid

def get_image_features(image_data):
    """
    获取图片的特征信息，用于更严格的图片查重
    
    Args:
        image_data (bytes): 图片二进制数据
    
    Returns:
        tuple: (image_hash, perceptual_hash, image_size)
    """
    try:
        # 1. 计算基本的MD5哈希
        image_hash = hashlib.md5(image_data).hexdigest()
        
        # 2. 计算感知哈希 (pHash)
        img = Image.open(BytesIO(image_data))
        # 转换为灰度图并调整大小为8x8
        img = img.convert('L').resize((8, 8), Image.Resampling.LANCZOS)
        pixels = list(img.getdata())
        avg = sum(pixels) / len(pixels)
        # 生成感知哈希值（1表示比平均值大，0表示比平均值小）
        perceptual_hash = ''.join(['1' if pixel > avg else '0' for pixel in pixels])
        
        # 3. 获取图片尺寸
        image_size = img.size
        
        return image_hash, perceptual_hash, image_size
    except Exception as e:
        print(f"Error calculating image features: {e}")
        return None, None, None

def is_similar_image(features1, features2):
    """
    判断两张图片是否相似
    
    Args:
        features1 (tuple): 第一张图片的特征 (image_hash, perceptual_hash, image_size)
        features2 (tuple): 第二张图片的特征 (image_hash, perceptual_hash, image_size)
    
    Returns:
        bool: 如果图片相似返回True，否则返回False
    """
    if not features1 or not features2:
        return False
        
    hash1, phash1, size1 = features1
    hash2, phash2, size2 = features2
    
    # 1. 如果启用MD5检查且MD5完全相同，认为是相同图片
    if CHECK_MD5_HASH and hash1 == hash2:
        print("图片MD5完全匹配，判定为重复")
        return True
    
    # 2. 检查感知哈希的汉明距离
    if phash1 and phash2:
        hamming_distance = sum(c1 != c2 for c1, c2 in zip(phash1, phash2))
        if hamming_distance <= PHASH_THRESHOLD:
            print(f"图片感知哈希相似度高（差异值：{hamming_distance}），判定为重复")
            return True
    
    # 3. 如果启用尺寸检查且尺寸完全相同，认为是相同图片
    if CHECK_IMAGE_SIZE and size1 and size2 and size1 == size2:
        print("图片尺寸完全相同，判定为重复")
        return True
        
    return False

def get_images_from_baidu(keyword, save_dir, park_image_features, park_name, season, is_cover=False):
    """
    从百度图片抓取指定数量符合要求的不重复图片
    
    Args:
        keyword (str): 搜索关键词
        save_dir (str): 保存目录
        park_image_features (list): 该公园已下载图片的特征列表
        park_name (str): 公园名称，用于更新CSV
        season (str): 季节或'cover'，用于更新CSV
        is_cover (bool): 是否是封面图片
    """
    header = HEADERS
    url = 'https://image.baidu.com/search/acjson?'
    n = 0
    checked_urls = 0 # Keep track of how many URLs we've checked

    # Try more pages if needed to find enough valid images
    max_pages_to_check = 5 # Limit how many pages we try
    current_page_num = 0

    target_count = IMAGES_PER_COVER if is_cover else IMAGES_PER_SEASON

    while n < target_count and current_page_num < max_pages_to_check:
        pn = current_page_num * BAIDU_RESULTS_PER_PAGE
        param = {
            'tn': 'resultjson_com',
            'logid': '7603311155072595725',
            'ipn': 'rj',
            'ct': 201326592,
            'is': '',
            'fp': 'result',
            'queryWord': keyword,
            'cl': 2,
            'lm': -1,
            'ie': 'utf-8',
            'oe': 'utf-8',
            'adpicid': '',
            'st': -1,
            'z': '',
            'ic': '',
            'hd': '',
            'latest': '',
            'copyright': '',
            'word': keyword,
            's': '',
            'se': '',
            'tab': '',
            'width': '',
            'height': '',
            'face': 0,
            'istype': 2,
            'qc': '',
            'nc': '1',
            'fr': '',
            'expermode': '',
            'force': '',
            'cg': '',
            'pn': pn,
            'rn': BAIDU_RESULTS_PER_PAGE,
            'gsm': '1e',
            '1618827096642': ''
        }
        print(f"Requesting page {current_page_num + 1} (starting at index {pn})...")
        try:
            request = requests.get(url=url, headers=header, params=param, timeout=REQUEST_TIMEOUT)
            request.raise_for_status()
            print(f'Request success for page {current_page_num + 1}.')
            request.encoding = 'utf-8'
            html = request.text
            image_url_list = re.findall('"thumbURL":"(.*?)",', html, re.S)
            if not image_url_list: 
                print("No more image URLs found on this page or subsequent pages.")
                break # Stop if no more images found
        except requests.exceptions.RequestException as e:
            print(f"Request failed for page {current_page_num + 1}: {e}")
            current_page_num += 1
            continue

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for image_url in image_url_list:
            checked_urls += 1
            if n >= target_count:
                print(f"Reached target of {target_count} images. Checked {checked_urls} URLs total.")
                return # Stop outer loop once enough images are found
            
            print(f"Attempting download ({n+1}/{target_count}): {image_url}")
            try:
                image_data = requests.get(url=image_url, headers=header, timeout=REQUEST_TIMEOUT).content
                
                # 1. Validate Resolution and Aspect Ratio
                if not is_image_valid(image_data, is_cover):
                    continue # Skip if invalid dimensions/ratio
                    
                # 2. 获取图片特征
                current_features = get_image_features(image_data)
                
                # 3. 检查是否与已下载的图片相似
                is_duplicate = False
                for existing_features in park_image_features:
                    if is_similar_image(current_features, existing_features):
                        print(f"Skipping similar image: {image_url}")
                        is_duplicate = True
                        break
                
                if is_duplicate:
                    continue
                    
                # 4. Save if valid and not duplicate
                park_image_features.append(current_features)
                with open(os.path.join(save_dir, f'{n:06d}.jpg'), 'wb') as fp:
                    fp.write(image_data)
                print(f"Successfully downloaded and saved image {n+1}/{target_count}: {os.path.join(save_dir, f'{n:06d}.jpg')}")
                
                # 5. Update CSV with image URL
                season_key = 'cover' if is_cover else season
                update_park_image_url(park_name, season_key, image_url)
                
                n = n + 1
                
            except requests.exceptions.RequestException as e:
                print(f"Error downloading image {image_url}: {e}")
            except Exception as e:
                print(f"Error processing image {image_url}: {e}")

        current_page_num += 1 # Move to next page
        
    if n < target_count:
        print(f"Warning: Could only download {n}/{target_count} valid images after checking {max_pages_to_check} pages and {checked_urls} URLs.")

def download_park_images(park_info, base_dir):
    """
    下载国家公园的四季和封面代表性图片
    
    Args:
        park_info (dict): 包含公园名称和描述的字典
        base_dir (str): 图片保存的基础目录
    """
    park_name = park_info['name']
    print(f"Processing park: {park_name}")
    
    # 用于存储该公园所有已下载图片的特征
    park_image_features = []
    
    # 首先下载封面图片
    print(f"Downloading cover photo for: {park_name}")
    cover_keyword = generate_cover_search_keyword(park_name, park_info['description'])
    print(f"Using cover search keyword: {cover_keyword}")
    
    # 在公园目录下创建封面图片目录
    cover_dir = os.path.join(base_dir, park_name, 'cover')
    if not os.path.exists(cover_dir):
        os.makedirs(cover_dir)
        
    get_images_from_baidu(cover_keyword, cover_dir, park_image_features, park_name, 'cover', is_cover=True)
    print(f"Completed downloading cover photo for: {park_name}")
    
    # 为每个季节下载图片
    for season in SEASONS.keys():
        print(f"Processing season: {season}")
        search_keyword = generate_search_keyword(park_name, park_info['description'], season)
        print(f"Using search keyword: {search_keyword}")
        
        # 在公园目录下创建季节子目录
        season_dir = os.path.join(base_dir, park_name, season)
        if not os.path.exists(season_dir):
            os.makedirs(season_dir)
            
        get_images_from_baidu(search_keyword, season_dir, park_image_features, park_name, season, is_cover=False)
        print(f"Completed downloading for {park_name} - {season}季")