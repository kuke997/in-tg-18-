import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def download_images_from_website(url, save_dir="downloaded_images"):
    """
    从指定网站下载图片
    
    参数:
    url (str): 目标网站URL
    save_dir (str): 图片保存目录
    """
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    
    # 设置请求头，模拟浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.google.com/",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        print(f"正在访问: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 检查robots.txt
        robots_url = urljoin(url, "/robots.txt")
        robots_response = requests.get(robots_url, headers=headers, timeout=5)
        if robots_response.status_code == 200:
            print("警告: 网站存在robots.txt文件")
            print("请检查爬取是否被允许:\n" + robots_response.text[:300] + "...")
        
        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有图片元素
        img_tags = soup.find_all('img')
        print(f"找到 {len(img_tags)} 个图片元素")
        
        # 下载图片
        downloaded = 0
        for i, img in enumerate(img_tags):
            try:
                # 获取图片URL（处理可能的data-src属性）
                img_url = img.get('src') or img.get('data-src')
                if not img_url:
                    continue
                    
                # 处理相对URL
                img_url = urljoin(url, img_url)
                
                # 过滤非图片URL
                if not img_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    continue
                
                # 获取图片内容
                print(f"正在下载 ({downloaded+1}/{len(img_tags)}): {img_url}")
                img_data = requests.get(img_url, headers=headers, timeout=15).content
                
                # 生成文件名
                filename = os.path.join(save_dir, f"image_{i+1}.{img_url.split('.')[-1]}")
                
                # 保存图片
                with open(filename, 'wb') as f:
                    f.write(img_data)
                
                downloaded += 1
                time.sleep(1)  # 礼貌性延迟，避免服务器压力
                
            except Exception as e:
                print(f"下载图片失败: {e}")
                continue
                
        print(f"下载完成! 成功下载 {downloaded} 张图片到目录: {save_dir}")
        
    except Exception as e:
        print(f"发生错误: {e}")

# 使用示例 - 请替换为实际需要分析的URL
if __name__ == "__main__":
    # 重要: 实际使用前请确认目标网站的爬取政策
    target_url = "https://example.com/safe-images"  # 替换为实际URL
    
    # 安全演示: 使用示例网站而不是原始请求的网站
    print("警告: 出于安全和法律考虑，此演示使用示例网站")
    print("实际使用请将target_url替换为实际URL")
    demo_url = "https://picsum.photos/images"  # 免费图片示例网站
    
    download_images_from_website(demo_url)
