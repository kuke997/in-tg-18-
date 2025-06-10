from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import requests
from urllib.parse import urljoin

def selenium_crawler(url, save_dir="downloaded_images"):
    # 设置Chrome选项
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 无头模式
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # 创建浏览器实例
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        print(f"正在访问: {url}")
        driver.get(url)
        time.sleep(5)  # 等待页面加载
        
        # 滚动页面加载更多内容
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # 获取页面源码
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 查找图片
        img_tags = soup.find_all('img')
        print(f"找到 {len(img_tags)} 个图片")
        
        # 下载图片
        downloaded = 0
        for i, img in enumerate(img_tags):
            src = img.get('src') or img.get('data-src')
            if src:
                try:
                    img_url = urljoin(url, src)
                    print(f"下载图片 {i+1}/{len(img_tags)}: {img_url}")
                    
                    response = requests.get(img_url, stream=True, timeout=15)
                    if response.status_code == 200:
                        # 保存图片
                        filename = os.path.join(save_dir, f"image_{i+1}.jpg")
                        with open(filename, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                        downloaded += 1
                        print(f"已保存: {filename}")
                    
                    time.sleep(1)  # 避免请求过快
                    
                except Exception as e:
                    print(f"下载失败: {e}")
        
        print(f"成功下载 {downloaded} 张图片")
        
    finally:
        driver.quit()

# 使用示例
if __name__ == "__main__":
    selenium_crawler("https://example.com")
