import os
import time
import requests
import re
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# 预定义的用户代理列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
]

def get_random_headers(referer=None):
    """生成随机的浏览器头信息"""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    if referer:
        headers["Referer"] = referer
    return headers

def download_images_from_website(url, save_dir="downloaded_images", max_retries=3):
    """
    高级图片爬虫 - 修复版
    
    参数:
    url (str): 目标网站URL
    save_dir (str): 图片保存目录
    max_retries (int): 最大重试次数
    """
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    
    try:
        print(f"正在访问: {url}")
        
        # 尝试访问目标页面
        for attempt in range(max_retries):
            try:
                headers = get_random_headers()
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                print(f"状态码: {response.status_code}")
                break  # 成功则退出重试循环
            except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
                if attempt < max_retries - 1:
                    wait = 2 ** attempt  # 指数退避
                    print(f"访问失败: {e}. 等待 {wait} 秒后重试 ({attempt+1}/{max_retries})")
                    time.sleep(wait)
                else:
                    raise  # 最后一次尝试失败则抛出异常
        
        # 检查内容类型
        content_type = response.headers.get('Content-Type', '').lower()
        if 'image' in content_type:
            # 直接下载图片
            print("检测到直接图片链接，直接下载")
            image_url = url
            filename = os.path.basename(urlparse(image_url).path
            if not filename:
                filename = "downloaded_image.jpg"
            save_path = os.path.join(save_dir, filename)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
                
            print(f"已保存: {save_path}")
            return 1
        
        # 检查robots.txt
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        try:
            robots_response = requests.get(robots_url, headers=get_random_headers(), timeout=5)
            if robots_response.status_code == 200:
                print("警告: 网站存在robots.txt文件")
                print("请检查爬取是否被允许:\n" + robots_response.text[:300] + "...")
        except Exception as e:
            print(f"检查robots.txt时出错: {e}")
        
        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有可能的图片元素
        img_tags = soup.find_all('img')
        print(f"找到 {len(img_tags)} 个img标签")
        
        # 收集所有可能的图片URL
        image_urls = set()
        
        # 1. 从img标签获取
        for img in img_tags:
            for attr in ['src', 'data-src', 'data-original', 'data-srcset', 'data-image']:
                img_url = img.get(attr)
                if img_url:
                    # 处理srcset属性 (多个URL)
                    if attr == 'srcset' or attr == 'data-srcset':
                        urls = [u.strip().split()[0] for u in img_url.split(',') if u.strip()]
                        for u in urls:
                            full_url = urljoin(url, u)
                            image_urls.add(full_url)
                    else:
                        full_url = urljoin(url, img_url.strip())
                        image_urls.add(full_url)
        
        # 2. 查找其他可能的图片容器
        for tag in soup.find_all(['div', 'figure', 'a', 'section']):
            # 检查背景图片
            style = tag.get('style', '')
            if style:
                match = re.search(r'url\(["\']?(.*?)["\']?\)', style, re.I)
                if match:
                    img_url = urljoin(url, match.group(1))
                    image_urls.add(img_url)
            
            # 检查数据属性
            for attr in ['data-src', 'data-image', 'data-url', 'data-original', 'href']:
                img_url = tag.get(attr)
                if img_url and any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    img_url = urljoin(url, img_url)
                    image_urls.add(img_url)
        
        print(f"总共找到 {len(image_urls)} 个可能的图片URL")
        
        # 下载图片
        downloaded = 0
        valid_urls = []
        
        # 先验证URL是否有效
        for img_url in image_urls:
            # 跳过非HTTP资源
            if not img_url.startswith('http'):
                continue
            
            # 跳过小图标
            if any(icon in img_url.lower() for icon in ['logo', 'icon', 'spacer', 'pixel', 'svg']):
                continue
            
            # 检查常见图片扩展名
            if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                valid_urls.append(img_url)
        
        print(f"经过过滤后，有 {len(valid_urls)} 个有效图片URL")
        
        # 下载有效图片
        for i, img_url in enumerate(valid_urls):
            try:
                # 随机延迟避免被封锁
                delay = random.uniform(0.5, 2.0)
                time.sleep(delay)
                
                # 更新头信息
                headers = get_random_headers(referer=url)
                
                # 下载图片
                print(f"正在下载 ({i+1}/{len(valid_urls)}): {img_url}")
                img_response = requests.get(img_url, headers=headers, timeout=20)
                
                # 检查状态码
                if img_response.status_code != 200:
                    print(f"跳过，状态码 {img_response.status_code}: {img_url}")
                    continue
                
                # 检查内容类型
                content_type = img_response.headers.get('Content-Type', '').lower()
                if not content_type or 'image' not in content_type:
                    print(f"跳过非图片内容 (Content-Type: {content_type}): {img_url}")
                    continue
                
                # 获取文件扩展名
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = 'jpg'
                elif 'png' in content_type:
                    ext = 'png'
                elif 'gif' in content_type:
                    ext = 'gif'
                elif 'webp' in content_type:
                    ext = 'webp'
                else:
                    # 尝试从URL获取扩展名
                    if img_url.lower().endswith('.png'):
                        ext = 'png'
                    elif img_url.lower().endswith('.gif'):
                        ext = 'gif'
                    elif img_url.lower().endswith('.webp'):
                        ext = 'webp'
                    else:
                        ext = 'jpg'  # 默认
                
                # 生成文件名
                filename = f"image_{i+1}.{ext}"
                save_path = os.path.join(save_dir, filename)
                
                # 避免覆盖
                counter = 1
                while os.path.exists(save_path):
                    base, ext = os.path.splitext(filename)
                    save_path = os.path.join(save_dir, f"{base}_{counter}{ext}")
                    counter += 1
                
                # 保存图片
                with open(save_path, 'wb') as f:
                    f.write(img_response.content)
                
                downloaded += 1
                print(f"已保存: {save_path}")
                
            except Exception as e:
                print(f"下载图片失败: {str(e)}")
                continue
                
        print(f"下载完成! 成功下载 {downloaded} 张图片到目录: {save_dir}")
        return downloaded
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return 0

# 使用示例
if __name__ == "__main__":
    print("高级图片爬虫 - 修复版")
    print("警告: 仅用于合法网站和技术研究目的")
    
    # 使用包含多个图片的测试页面
    target_url = "https://www.pexels.com/search/nature/"
    
    # 或者使用维基百科的图片页面
    # target_url = "https://en.wikipedia.org/wiki/Nature"
    
    # 或者使用直接图片链接测试
    # target_url = "https://picsum.photos/2000/1000"
    
    print(f"使用测试网站: {target_url}")
    downloaded_count = download_images_from_website(target_url)
    
    if downloaded_count == 0:
        print("\n如果仍然无法下载图片，请尝试:")
        print("1. 检查网络连接和代理设置")
        print("2. 尝试不同的目标网站")
        print("3. 查看网站是否使用JavaScript加载图片")
        print("4. 检查防火墙或安全软件设置")
        
        # 提供备用方案
        print("\n备用方案：使用简单的图片下载函数")
        simple_image_downloader()
    else:
        print("\n爬虫成功运行！")

def simple_image_downloader():
    """简单的图片下载器 - 直接下载测试图片"""
    save_dir = "downloaded_images"
    os.makedirs(save_dir, exist_ok=True)
    
    # 测试图片URL
    test_images = [
        "https://picsum.photos/2000/1000",
        "https://picsum.photos/2000/1000?image=1",
        "https://picsum.photos/2000/1000?image=2"
    ]
    
    print("\n使用简单图片下载器下载测试图片...")
    
    for i, img_url in enumerate(test_images):
        try:
            response = requests.get(img_url, timeout=10)
            if response.status_code == 200:
                filename = os.path.join(save_dir, f"test_image_{i+1}.jpg")
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"已保存测试图片: {filename}")
            else:
                print(f"下载失败，状态码 {response.status_code}: {img_url}")
        except Exception as e:
            print(f"下载测试图片失败: {str(e)}")
    
    print("简单图片下载完成")
