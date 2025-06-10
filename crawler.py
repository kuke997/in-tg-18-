import requests
from bs4 import BeautifulSoup
import json
import logging

CACHE_FILE = 'img_cache.json'
SITE_URL = 'https://www.photos18.com/'

logger = logging.getLogger(__name__)

def fetch_image_links(limit=20):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(SITE_URL, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'lxml')

        img_tags = soup.select('div.card-image img')
        urls = []
        for img in img_tags:
            src = img.get('data-src') or img.get('src')
            if src and src.startswith('http') and src.lower().endswith(('.jpg', '.jpeg', '.png')):
                urls.append(src)
            if len(urls) >= limit:
                break

        logger.info(f"Fetched {len(urls)} image URLs from {SITE_URL}")
        if urls:
            logger.info(f"Sample URLs: {urls[:3]}")
        return urls

    except Exception as e:
        logger.error(f"Error fetching images from {SITE_URL}: {e}")
        return []

def update_cache():
    links = fetch_image_links()
    if links:
        with open(CACHE_FILE, 'w') as f:
            json.dump(links, f, indent=2)
        logger.info(f"Cache updated with {len(links)} URLs")
    else:
        logger.warning("No links fetched; cache not updated")
