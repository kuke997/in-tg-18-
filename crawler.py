import asyncio
import json
import os
from playwright.async_api import async_playwright

BASE_URL = "https://www.photos18.com"
CACHE_FILE = "img_cache.json"

async def get_category_links(page):
    await page.goto(f"{BASE_URL}", timeout=60000)
    await page.wait_for_selector("a.nav-link[href*='/cat/']", timeout=10000)
    links = await page.eval_on_selector_all("a.nav-link[href*='/cat/']", "els => els.map(el => el.href)")
    return list(set(links))

async def get_all_post_links(page, category_url):
    post_links = []
    page_num = 1
    while True:
        url = f"{category_url}/page/{page_num}" if page_num > 1 else category_url
        try:
            await page.goto(url, timeout=60000)
            items = await page.query_selector_all("div.item > a")
            if not items:
                break
            for item in items:
                href = await item.get_attribute("href")
                if href and href.startswith("/v/"):
                    full_url = BASE_URL + href
                    post_links.append(full_url)
            page_num += 1
        except:
            break
    return post_links

async def extract_images_from_post(page, post_url):
    await page.goto(post_url, timeout=60000)
    await page.wait_for_timeout(2000)  # 等待 js 加载
    img_urls = await page.eval_on_selector_all("a[data-fancybox='gallery']", "els => els.map(el => el.href)")
    return [img for img in img_urls if img.endswith(('.jpg', '.jpeg', '.png', '.webp'))]

async def main():
    all_images = set()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        categories = await get_category_links(page)
        print(f"共发现 {len(categories)} 个分类")

        for cat in categories:
            print(f"抓取分类: {cat}")
            posts = await get_all_post_links(page, cat)
            print(f"  - 共找到 {len(posts)} 个帖子")
            for post in posts:
                imgs = await extract_images_from_post(page, post)
                print(f"    - 帖子: {post} → {len(imgs)} 张图片")
                all_images.update(imgs)
        await browser.close()

    # 保存缓存
    all_images = list(all_images)
    with open(CACHE_FILE, "w") as f:
        json.dump(all_images, f, indent=2)
    print(f"\n✅ 共抓取到 {len(all_images)} 张图片，已保存到 {CACHE_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
