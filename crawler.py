import requests
from bs4 import BeautifulSoup
import json
import logging

CACHE_FILE = 'img_cache.json'
SITE_URL = 'https://www.photos18.com/'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

        logging.info(f"Fetched {len(urls)} image URLs")
        return urls

    except Exception as e:
        logging.error(f"Error fetching images: {e}")
        return []

def update_cache():
    links = fetch_image_links()
    if links:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(links, f, indent=2, ensure_ascii=False)
        logging.info(f"Cache updated with {len(links)} images")
    else:
        logging.warning("No images fetched; cache not updated")

if __name__ == "__main__":
    update_cache()
