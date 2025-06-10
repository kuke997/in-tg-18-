import requests
from bs4 import BeautifulSoup
import json
import logging
import os

CACHE_FILE = 'img_cache.json'
SITE_URL = 'https://www.photos18.com/'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_image_links(limit=20):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(SITE_URL, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'lxml')

        # 先按 card-image 结构抓
        img_tags = soup.select('div.card-image img')
        urls = [img.get('data-src') or img.get('src') for img in img_tags]
        urls = [u for u in urls if u and u.startswith('http')][:limit]

        # fallback：如果没抓到，改用全局 <img>
        if not urls:
            logging.warning("Primary selector 没抓到图片，尝试全局 <img> fallback")
            all_tags = soup.find_all('img')
            for img in all_tags:
                src = img.get('data-src') or img.get('src')
                if src and src.startswith('http'):
                    urls.append(src)
                if len(urls) >= limit:
                    break

        logging.info(f"Fetched {len(urls)} image URLs")
        return urls

    except Exception as e:
        logging.error(f"Error fetching images: {e}")
        return []

def update_cache():
    links = fetch_image_links()
    # 总是写入缓存文件，避免旧数据或空文件导致 JSONDecodeError
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(links, f, indent=2, ensure_ascii=False)
    if links:
        logging.info(f"Cache updated with {len(links)} images")
    else:
        logging.warning("Cache overwritten with empty list (no images)")

if __name__ == "__main__":
    update_cache()
