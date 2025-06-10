import requests
from bs4 import BeautifulSoup
import json
import logging

CACHE_FILE = 'img_cache.json'
SITE_URL = 'https://www.photos18.com/'

logger = logging.getLogger(__name__)

def fetch_image_links(limit=20):
    """
    爬取 photos18.com 首页的图片链接
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(SITE_URL, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'lxml')

        # 根据实际页面结构，photos18 的缩略图通常在 <div class="card-image"> 内的 <img>
        # 请在浏览器中检查 class 名，以下仅示例
        img_tags = soup.select('div.card-image img')
        urls = []
        for img in img_tags:
            src = img.get('data-src') or img.get('src')
            if src and src.startswith('http') and src.lower().endswith(('.jpg', '.jpeg', '.png')):
                urls.append(src)
            if len(urls) >= limit:
                break

        logger.info("Fetched %d image URLs from %s", len(urls), SITE_URL)
        if urls:
            logger.info("Sample URLs: %s", urls[:3])
        return urls

    except Exception as e:
        logger.error("Error fetching images from %s: %s", SITE_URL, e)
        return []

def update_cache():
    links = fetch_image_links()
    if links:
        with open(CACHE_FILE, 'w') as f:
            json.dump(links, f, indent=2)
        logger.info("Cache updated with %d URLs", len(links))
    else:
        logger.warning("No links fetched; cache not updated")
