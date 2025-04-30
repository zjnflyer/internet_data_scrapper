"""
National Parks Image Scraper

Main program to download representative images of Chinese National Parks from Baidu Image Search.
"""

import os
from src.baidu_scrapper_valid import get_national_parks, download_park_images
# Import config settings
from src.config import IMAGES_BASE_DIR

def main():
    # Get list of national parks with their descriptions
    parks_info = get_national_parks()
    
    # Set up base directory for images using config
    base_dir = IMAGES_BASE_DIR
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Download images for each national park
    for park_info in parks_info:
        # Pass base_dir from config. page_num is no longer needed.
        download_park_images(park_info, base_dir)
        print("-" * 50)  # 添加分隔线，使输出更清晰

if __name__ == "__main__":
    main() 