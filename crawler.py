import requests
from bs4 import BeautifulSoup
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
BASE_URL = "https://www.photos18.com"
CACHE_FILE = "img_cache.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

def get_category_urls():
    url = BASE_URL + "/cat"
    logging.info(f"抓取分类页: {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
    except Exception as e:
        logging.error(f"请求分类页失败: {e}")
        return []

    soup = BeautifulSoup(r.text, "lxml")
    links = soup.select("div.cate-list a")  # 修改此处
    urls = []
    for a in links:
        href = a.get("href")
        if href:
            if href.startswith("http"):
                urls.append(href)
            else:
                urls.append(BASE_URL + href)
    logging.info(f"共找到 {len(urls)} 个分类链接")
    return urls

def get_max_page_from_category(category_url):
    logging.info(f"获取分页信息: {category_url}")
    try:
        r = requests.get(category_url, headers=HEADERS, timeout=10)
        r.raise_for_status()
    except Exception as e:
        logging.error(f"请求分类页失败: {e}")
        return 1

    soup = BeautifulSoup(r.text, "lxml")
    page_links = soup.select("div.pagination a")  # 修改此处
    max_page = 1
    for a in page_links:
        try:
            page_num = int(a.text.strip())
            if page_num > max_page:
                max_page = page_num
        except:
            pass
    logging.info(f"最大分页数: {max_page}")
    return max_page

def fetch_post_urls_from_list_page(url):
    logging.info(f"抓取列表页: {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
    except Exception as e:
        logging.error(f"请求列表页失败: {e}")
        return []

    soup = BeautifulSoup(r.text, "lxml")
    links = soup.select(".post-list .post-item a")  # 修改此处，适配列表页文章链接
    post_urls = []
    for link in links:
        href = link.get("href")
        if href:
            if href.startswith("http"):
                post_urls.append(href)
            else:
                post_urls.append(BASE_URL + href)
    if not post_urls:
        logging.info("列表页无文章链接，提前结束")
    return post_urls

def fetch_images_from_post(post_url):
    logging.info(f"抓取详情页图片: {post_url}")
    try:
        r = requests.get(post_url, headers=HEADERS, timeout=10)
        r.raise_for_status()
    except Exception as e:
        logging.error(f"请求详情页失败: {e}")
        return []

    soup = BeautifulSoup(r.text, "lxml")
    images = []
    img_tags = soup.select("div.post-content img")  # 修改此处
    for img in img_tags:
        src = img.get("data-src") or img.get("src")
        if src and src.startswith("http"):
            images.append(src)
    return images

def crawl_all_images():
    all_images = set()
    category_urls = get_category_urls()
    for category_url in category_urls:
        max_page = get_max_page_from_category(category_url)
        for page_num in range(1, max_page + 1):
            if page_num == 1:
                url = category_url
            else:
                url = f"{category_url}?page={page_num}"  # 修改分页格式
            post_urls = fetch_post_urls_from_list_page(url)
            if not post_urls:
                break
            for post_url in post_urls:
                imgs = fetch_images_from_post(post_url)
                all_images.update(imgs)
                time.sleep(1)  # 防封
    return list(all_images)

def update_cache():
    imgs = crawl_all_images()
    if imgs:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(imgs, f, indent=2, ensure_ascii=False)
        logging.info(f"共抓取到 {len(imgs)} 张图片，写入缓存")
    else:
        logging.warning("未抓取到任何图片，缓存未更新")

if __name__ == "__main__":
    update_cache()
