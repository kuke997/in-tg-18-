import requests
from bs4 import BeautifulSoup
import json
import logging
import time
from urllib.parse import urljoin, urlparse

CACHE_FILE = 'img_cache.json'
BASE_URL = 'https://www.photos18.com'

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
MAX_PAGES = 10  # 限制爬取页数，避免无限爬

def get_soup(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, 'lxml')
    except Exception as e:
        logging.error(f"请求失败 {url}: {e}")
        return None

def parse_article_links(page_url):
    """
    解析列表页，获取所有文章链接
    """
    soup = get_soup(page_url)
    if not soup:
        return []

    links = []
    # 观察页面结构：文章列表中，文章链接通常在 <a> 标签里，有特定 class，比如 'post-title' 或 'entry-title'
    # 这里以 <h2 class="post-title"><a href="文章链接"> 为例
    posts = soup.select('h2.post-title a')
    for a in posts:
        href = a.get('href')
        if href:
            full_url = urljoin(BASE_URL, href)
            links.append(full_url)
    return links

def parse_images_from_article(article_url):
    """
    解析文章详情页，获取所有图片链接
    """
    soup = get_soup(article_url)
    if not soup:
        return []

    img_urls = []
    # 根据页面观察，正文图片一般在 <div class="entry-content"> 里面的 <img>
    content_div = soup.select_one('div.entry-content')
    if content_div:
        imgs = content_div.find_all('img')
        for img in imgs:
            src = img.get('data-src') or img.get('src') or ''
            if src.startswith('http') and src.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_urls.append(src)
    else:
        logging.warning(f"未找到内容区，文章页 {article_url}")

    return img_urls

def crawl_all_images(max_pages=MAX_PAGES):
    all_images = set()
    for page_num in range(1, max_pages + 1):
        page_url = f"{BASE_URL}/page/{page_num}"
        logging.info(f"抓取列表页: {page_url}")

        article_links = parse_article_links(page_url)
        if not article_links:
            logging.info("列表页无文章链接，提前结束")
            break

        for article_url in article_links:
            logging.info(f"抓取文章页: {article_url}")
            imgs = parse_images_from_article(article_url)
            logging.info(f"文章页抓取到 {len(imgs)} 张图片")
            for img_url in imgs:
                all_images.add(img_url)
            time.sleep(1)  # 避免请求过快

        time.sleep(2)  # 列表页之间间隔

    return list(all_images)

def update_cache():
    imgs = crawl_all_images()
    logging.info(f"共抓取到 {len(imgs)} 张图片，写入缓存")
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(imgs, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    update_cache()
