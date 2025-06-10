from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json
import os
import logging

BASE_URL = "https://www.photos18.com"
CACHE_FILE = "img_cache.json"

logging.basicConfig(level=logging.INFO)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

def get_all_category_urls():
    driver.get(BASE_URL)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "lxml")
    links = soup.select("ul.nav > li > a")
    category_urls = [urljoin(BASE_URL, a["href"]) for a in links if "/cat/" in a["href"]]
    logging.info(f"发现 {len(category_urls)} 个分类")
    return category_urls

def get_all_post_urls_from_category(category_url, max_pages=5):
    post_urls = []
    for page in range(1, max_pages + 1):
        page_url = f"{category_url}/page/{page}" if page > 1 else category_url
        logging.info(f"浏览分类分页: {page_url}")
        try:
            driver.get(page_url)
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, "lxml")
            posts = soup.select("div.item > a")
            if not posts:
                break
            for post in posts:
                href = post.get("href")
                if href:
                    full_url = urljoin(BASE_URL, href)
                    post_urls.append(full_url)
        except Exception as e:
            logging.error(f"分页失败: {e}")
            continue
    return post_urls

def extract_images_from_post(post_url):
    logging.info(f"抓取详情页: {post_url}")
    try:
        driver.get(post_url)
        time.sleep(3)
        thumbnails = driver.find_elements(By.CSS_SELECTOR, ".gallery img")
        image_urls = []

        for thumb in thumbnails:
            try:
                thumb.click()
                time.sleep(1)
                img = driver.find_element(By.CSS_SELECTOR, ".fancybox-image")
                img_url = img.get_attribute("src")
                if img_url:
                    image_urls.append(img_url)
                driver.find_element(By.CSS_SELECTOR, "button.fancybox-button--close").click()
                time.sleep(1)
            except Exception as e:
                logging.warning(f"图片弹窗失败: {e}")
                continue

        return image_urls
    except Exception as e:
        logging.error(f"详情页抓取失败: {e}")
        return []

def crawl_full_site():
    all_images = set()
    categories = get_all_category_urls()
    for cat_url in categories:
        posts = get_all_post_urls_from_category(cat_url, max_pages=3)
        for post_url in posts:
            imgs = extract_images_from_post(post_url)
            all_images.update(imgs)
    return list(all_images)

def update_cache():
    imgs = crawl_full_site()
    if imgs:
        with open(CACHE_FILE, "w") as f:
            json.dump(imgs, f, indent=2)
        logging.info(f"抓取完成，保存 {len(imgs)} 张图片")
    else:
        logging.warning("没有抓取到任何图片")

if __name__ == "__main__":
    update_cache()
    driver.quit()
