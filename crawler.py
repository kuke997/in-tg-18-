import requests
from bs4 import BeautifulSoup
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
BASE_URL = "https://www.sex.com/en/gifs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}
CACHE_FILE = "sex_gifs_cache.json"

def fetch_gifs_from_page(page_num):
    url = f"{BASE_URL}?page={page_num}"
    logging.info(f"抓取第 {page_num} 页: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logging.error(f"请求失败: {e}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    gifs = []

    # gif图通常在 <img> 标签，且src或data-src是.gif结尾的
    img_tags = soup.select("img")
    for img in img_tags:
        src = img.get("data-src") or img.get("src")
        if src and src.endswith(".gif"):
            # 补全URL，防止相对路径
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = "https://www.sex.com" + src
            gifs.append(src)
    return gifs

def crawl_all_gifs(max_pages=50):
    all_gifs = set()
    for page in range(1, max_pages + 1):
        gifs = fetch_gifs_from_page(page)
        if not gifs:
            logging.info(f"第 {page} 页无新gif，停止爬取。")
            break
        logging.info(f"第 {page} 页抓取到 {len(gifs)} 个gif")
        all_gifs.update(gifs)
        time.sleep(1)
    return list(all_gifs)

def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    logging.info(f"已保存 {len(data)} 个gif到缓存文件: {CACHE_FILE}")

if __name__ == "__main__":
    gifs = crawl_all_gifs()
    if gifs:
        save_cache(gifs)
    else:
        logging.warning("没有抓取到任何gif图片")
