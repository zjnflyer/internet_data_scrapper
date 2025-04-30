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
# Add imports for image processing
from io import BytesIO
from PIL import Image
from .config import (
    IMAGES_PER_PARK,
    DATA_FILE_PATH,
    REQUEST_TIMEOUT,
    BAIDU_RESULTS_PER_PAGE,
    HEADERS,
    LANDSCAPE_FEATURES,
    DEFAULT_KEYWORD_SUFFIX,
    MAX_FEATURES_IN_KEYWORD,
    # Import new config variables
    MIN_RESOLUTION,
    ASPECT_RATIO_RANGE
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

def generate_search_keyword(park_name, description):
    """
    生成优化的搜索关键词
    """
    features = extract_key_features(description)
    if features:
        # Use max features defined in config
        features = features[:MAX_FEATURES_IN_KEYWORD]
        search_keyword = f"{park_name} 风景 {' '.join(features)}"
    else:
        # Use default suffix from config
        search_keyword = f"{park_name} {DEFAULT_KEYWORD_SUFFIX}"
    return search_keyword

def get_national_parks():
    """
    从CSV文件读取国家公园信息
    """
    # Use data file path from config
    df = pd.read_csv(DATA_FILE_PATH)
    return [{'name': row['名称'], 'description': row['描述']} for _, row in df.iterrows()]

def is_image_valid(image_data):
    """Check if image meets resolution and aspect ratio requirements."""
    try:
        img = Image.open(BytesIO(image_data))
        width, height = img.size

        # 1. Resolution Check
        if MIN_RESOLUTION and MIN_RESOLUTION != (0, 0):
            if width < MIN_RESOLUTION[0] or height < MIN_RESOLUTION[1]:
                print(f"Skipping image: Resolution ({width}x{height}) below minimum ({MIN_RESOLUTION[0]}x{MIN_RESOLUTION[1]})")
                return False

        # 2. Aspect Ratio Check
        if ASPECT_RATIO_RANGE:
            if height == 0: # Avoid division by zero
                print("Skipping image: Height is 0")
                return False 
            aspect_ratio = width / height
            min_ratio, max_ratio = ASPECT_RATIO_RANGE
            if not (min_ratio <= aspect_ratio <= max_ratio):
                print(f"Skipping image: Aspect ratio ({aspect_ratio:.2f}) outside range [{min_ratio}-{max_ratio}]")
                return False
                
        return True # All checks passed

    except Exception as e:
        print(f"Error validating image: {e}")
        return False # Treat validation errors as invalid

def get_images_from_baidu(keyword, page_num, save_dir):
    """
    从百度图片抓取指定数量符合要求的不重复图片
    """
    header = HEADERS
    url = 'https://image.baidu.com/search/acjson?'
    n = 0
    hash_set = set()
    checked_urls = 0 # Keep track of how many URLs we've checked

    # Try more pages if needed to find enough valid images
    max_pages_to_check = 5 # Limit how many pages we try
    current_page_num = 0

    while n < IMAGES_PER_PARK and current_page_num < max_pages_to_check:
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
            if n >= IMAGES_PER_PARK:
                print(f"Reached target of {IMAGES_PER_PARK} images. Checked {checked_urls} URLs total.")
                return # Stop outer loop once enough images are found
            
            print(f"Attempting download ({n+1}/{IMAGES_PER_PARK}): {image_url}")
            try:
                image_data = requests.get(url=image_url, headers=header, timeout=REQUEST_TIMEOUT).content
                
                # 1. Validate Resolution and Aspect Ratio
                if not is_image_valid(image_data):
                    continue # Skip if invalid dimensions/ratio
                    
                # 2. Check for Duplicates (Hash)
                image_hash = hashlib.md5(image_data).hexdigest()
                if image_hash in hash_set:
                    print(f"Skipping duplicate image (hash): {image_url}")
                    continue
                    
                # 3. Save if valid and not duplicate
                hash_set.add(image_hash)
                with open(os.path.join(save_dir, f'{n:06d}.jpg'), 'wb') as fp:
                    fp.write(image_data)
                print(f"Successfully downloaded and saved image {n+1}/{IMAGES_PER_PARK}: {os.path.join(save_dir, f'{n:06d}.jpg')}")
                n = n + 1
                
            except requests.exceptions.RequestException as e:
                print(f"Error downloading image {image_url}: {e}")
            except Exception as e:
                print(f"Error processing image {image_url}: {e}")

        current_page_num += 1 # Move to next page
        
    if n < IMAGES_PER_PARK:
        print(f"Warning: Could only download {n}/{IMAGES_PER_PARK} valid images after checking {max_pages_to_check} pages and {checked_urls} URLs.")

def download_park_images(park_info, base_dir):
    """
    下载国家公园的代表性图片
    
    Args:
        park_info (dict): 包含公园名称和描述的字典
        base_dir (str): 图片保存的基础目录
    """
    park_name = park_info['name']
    print(f"Processing park: {park_name}")
    search_keyword = generate_search_keyword(park_name, park_info['description'])
    print(f"Using search keyword: {search_keyword}")
    save_dir = os.path.join(base_dir, park_name)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # page_num is handled internally by get_images_from_baidu now
    get_images_from_baidu(search_keyword, 1, save_dir) 
    print(f"Completed downloading for: {park_name}")