import requests
from bs4 import BeautifulSoup
import json

CACHE_FILE = 'img_cache.json'
SITE_URL = 'https://www.photos18.com/'

def fetch_image_links():
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(SITE_URL, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, 'lxml')
    img_tags = soup.select('img[src^="https://cdn"]')
    return [img['src'] for img in img_tags if img['src'].endswith(('.jpg', '.jpeg', '.png'))][:20]

def update_cache():
    links = fetch_image_links()
    with open(CACHE_FILE, 'w') as f:
        json.dump(links, f)

