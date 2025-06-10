import requests
from bs4 import BeautifulSoup
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
BASE_URL = "https://www.photos18.com"
CACHE_FILE = "img_cache.json"

def fetch_post_urls(page_num):
    url = f"{BASE_URL}/page/{page_num}"
    logging.info(f"抓取列表页: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except Exception as e:
        logging.error(f"请求列表页失败: {e}")
        return []

    soup = BeautifulSoup(r.text, "lxml")
    # 根据页面结构获取文章链接，下面是示例selector，可能需要调整
    links = soup.select("div.post-item > a")
    post_urls = []
    for link in links:
        href = link.get("href")
        if href and href.startswith(BASE_URL):
            post_urls.append(href)
        elif href:
            post_urls.append(BASE_URL + href)

    if not post_urls:
        logging.info("列表页无文章链接，提前结束")
    return post_urls

def fetch_images_from_post(post_url):
    logging.info(f"抓取详情页图片: {post_url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(post_url, headers=headers, timeout=10)
        r.raise_for_status()
    except Exception as e:
        logging.error(f"请求详情页失败: {e}")
        return []

    soup = BeautifulSoup(r.text, "lxml")
    # 按实际结构抓取图片，以下selector仅示例，需根据具体网页结构修改
    images = []
    img_tags = soup.select("div.gallery img")
    for img in img_tags:
        src = img.get("data-src") or img.get("src")
        if src and src.startswith("http"):
            images.append(src)

    return images

def crawl_all_images(max_pages=10):
    all_images = []
    for page in range(1, max_pages + 1):
        post_urls = fetch_post_urls(page)
        if not post_urls:
            break
        for post_url in post_urls:
            imgs = fetch_images_from_post(post_url)
            all_images.extend(imgs)
            time.sleep(1)  # 礼貌爬取，避免被封
    return list(set(all_images))  # 去重

def update_cache():
    imgs = crawl_all_images(max_pages=5)
    if imgs:
        with open(CACHE_FILE, "w") as f:
            json.dump(imgs, f, indent=2)
        logging.info(f"共抓取到 {len(imgs)} 张图片，写入缓存")
    else:
        logging.warning("未抓取到任何图片，缓存未更新")

if __name__ == "__main__":
    update_cache()
