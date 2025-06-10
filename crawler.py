from playwright.sync_api import sync_playwright
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
BASE_URL = "https://www.sex.com/en/gifs"
CACHE_FILE = "sex_gifs_cache.json"

def crawl_gifs(max_pages=10):
    all_gifs = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for page_num in range(1, max_pages + 1):
            url = f"{BASE_URL}?page={page_num}"
            logging.info(f"访问页面 {url}")
            page.goto(url)
            time.sleep(3)  # 等待js加载
            # 查询所有gif图片
            imgs = page.query_selector_all("img[src$='.gif']")
            if not imgs:
                logging.info(f"第 {page_num} 页无gif，停止抓取。")
                break
            for img in imgs:
                src = img.get_attribute("src")
                if src:
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        src = "https://www.sex.com" + src
                    all_gifs.add(src)
            logging.info(f"第 {page_num} 页抓取到 {len(imgs)} 张gif")
            time.sleep(1)
        browser.close()
    return list(all_gifs)

def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    logging.info(f"已保存 {len(data)} 个gif到缓存文件: {CACHE_FILE}")

if __name__ == "__main__":
    gifs = crawl_gifs()
    if gifs:
        save_cache(gifs)
    else:
        logging.warning("没有抓取到任何gif图片")
