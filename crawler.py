import requests
from bs4 import BeautifulSoup
import time
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "https://www.photos18.com"
START_PAGE = 1
MAX_PAGES = 10  # 爬取前10页列表页，改成你想爬的页数
OUTPUT_FILE = "all_image_links.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

def get_list_page_urls(page_num):
    return f"{BASE_URL}/page/{page_num}"

def fetch_article_links_from_list(page_num):
    url = get_list_page_urls(page_num)
    logging.info(f"抓取列表页: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logging.error(f"请求列表页失败 {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, 'lxml')

    # 列表页文章链接，通常在 article 标签内的 h2 a
    articles = soup.select('article h2 a')
    links = []
    for a in articles:
        href = a.get('href')
        if href and href.startswith(BASE_URL):
            links.append(href)
        elif href:
            links.append(BASE_URL + href)
    logging.info(f"列表页抓取到 {len(links)} 篇文章链接")
    return links

def fetch_images_from_article(article_url):
    logging.info(f"抓取详情页图片: {article_url}")
    try:
        resp = requests.get(article_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logging.error(f"请求详情页失败 {article_url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, 'lxml')

    # 重点：找 gallery 容器里的大图链接
    gallery = soup.select_one('#gallery-1')
    if not gallery:
        logging.warning(f"{article_url} 没找到 gallery-1 容器，尝试其他方法")

        # 备选：抓取文章正文所有 <img> 标签
        imgs = soup.select('article img')
        img_urls = []
        for img in imgs:
            src = img.get('data-src') or img.get('src')
            if src and src.startswith('http'):
                img_urls.append(src)
        return img_urls

    anchors = gallery.select('figure.gallery-item a')
    img_urls = []
    for a in anchors:
        href = a.get('href')
        if href and href.startswith('http'):
            img_urls.append(href)
    logging.info(f"详情页抓取到 {len(img_urls)} 张图片")
    return img_urls

def main():
    all_images = []

    for page in range(START_PAGE, START_PAGE + MAX_PAGES):
        article_links = fetch_article_links_from_list(page)
        if not article_links:
            logging.info("当前列表页无文章链接，提前结束爬取")
            break

        for article_url in article_links:
            imgs = fetch_images_from_article(article_url)
            all_images.extend(imgs)
            time.sleep(1)  # 礼貌等待，避免被封禁

        time.sleep(2)  # 等待下一列表页请求

    # 去重
    all_images = list(set(all_images))
    logging.info(f"全站爬取共计 {len(all_images)} 张图片")

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_images, f, indent=2)

    logging.info(f"图片链接写入文件: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
