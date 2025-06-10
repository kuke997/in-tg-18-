import requests
from bs4 import BeautifulSoup
import json
import logging
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

BASE_URL = "https://www.photos18.com"
START_PAGE = 1
MAX_PAGES = 5  # 你可以调大页数，测试时先用小一点的
CACHE_FILE = "all_image_links.json"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def get_page_urls(page_num):
    url = f"{BASE_URL}/page/{page_num}"
    logging.info(f"抓取列表页: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logging.error(f"请求列表页失败: {e}")
        return []
    soup = BeautifulSoup(resp.text, "lxml")

    # 这里根据网站实际结构改选择器，列表页文章链接都在 <a href="xxx" class="title"> 里（示例）
    links = []
    for a_tag in soup.select("h3 a"):  # 你用浏览器检查具体是哪儿，改这里的选择器
        href = a_tag.get("href")
        if href and href.startswith(BASE_URL):
            links.append(href)
        elif href and href.startswith("/v/"):
            links.append(BASE_URL + href)
    logging.info(f"找到 {len(links)} 篇文章链接")
    return links

def get_images_from_post(post_url):
    logging.info(f"抓取详情页: {post_url}")
    try:
        resp = requests.get(post_url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logging.error(f"请求详情页失败: {e}")
        return []
    soup = BeautifulSoup(resp.text, "lxml")

    # 这里的图片一般在 <div id="gallery-1"> 中的 <a href="图片地址">，也可能是 <img src="图片地址">
    images = []
    gallery_div = soup.find("div", id="gallery-1")
    if gallery_div:
        for a in gallery_div.find_all("a"):
            href = a.get("href")
            if href and href.lower().endswith((".jpg", ".jpeg", ".png")):
                images.append(href)
    else:
        # 如果没有 gallery-1，尝试找所有 img 标签里的图片
        imgs = soup.find_all("img")
        for img in imgs:
            src = img.get("src") or img.get("data-src")
            if src and src.lower().endswith((".jpg", ".jpeg", ".png")):
                if src.startswith("/"):
                    src = BASE_URL + src
                images.append(src)
    logging.info(f"详情页抓取到 {len(images)} 张图片")
    return images

def crawl_all_images():
    all_images = set()
    for page_num in range(START_PAGE, START_PAGE + MAX_PAGES):
        post_urls = get_page_urls(page_num)
        if not post_urls:
            logging.info("列表页无文章链接，提前结束")
            break

        for post_url in po_
