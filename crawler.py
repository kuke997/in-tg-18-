import os
import time
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def download_images_from_website(url, save_dir="downloaded_images"):
    """
    从指定网站下载图片 - 修复版
    
    参数:
    url (str): 目标网站URL
    save_dir (str): 图片保存目录
    """
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    
    # 设置请求头，模拟浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": url,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    
    try:
        print(f"正在访问: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 检查robots.txt
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        try:
            robots_response = requests.get(robots_url, headers=headers, timeout=5)
            if robots_response.status_code == 200:
                print("警告: 网站存在robots.txt文件")
                print("请检查爬取是否被允许:\n" + robots_response.text[:300] + "...")
        except Exception as e:
            print(f"检查robots.txt时出错: {e}")
        
        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有可能的图片元素 - 多种方式
        img_tags = soup.find_all('img')
        print(f"找到 {len(img_tags)} 个img标签")
        
        # 额外的查找方式
        image_divs = soup.find_all('div', class_=re.compile(r'image|img|photo|pic', re.I))
        print(f"找到 {len(image_divs)} 个图片容器")
        
        # 收集所有可能的图片URL
        image_urls = set()
        
        # 1. 从img标签获取
        for img in img_tags:
            for attr in ['src', 'data-src', 'data-original', 'data-srcset', 'data-image']:
                img_url = img.get(attr)
                if img_url:
                    # 处理srcset属性
                    if attr == 'data-srcset':
                        # 取第一个URL
                        img_url = img_url.split(',')[0].split()[0]
                    
                    # 处理相对URL
                    img_url = urljoin(url, img_url.strip())
                    
                    # 添加到集合
                    image_urls.add(img_url)
        
        # 2. 从图片容器获取
        for div in image_divs:
            # 检查背景图片
            style = div.get('style', '')
            if style:
                match = re.search(r'url\(["\']?(.*?)["\']?\)', style, re.I)
                if match:
                    img_url = urljoin(url, match.group(1))
                    image_urls.add(img_url)
            
            # 检查数据属性
            for attr in ['data-src', 'data-image', 'data-url']:
                img_url = div.get(attr)
                if img_url:
                    img_url = urljoin(url, img_url)
                    image_urls.add(img_url)
        
        print(f"总共找到 {len(image_urls)} 个可能的图片URL")
        
        # 下载图片
        downloaded = 0
        for i, img_url in enumerate(image_urls):
            try:
                # 跳过非HTTP资源
                if not img_url.startswith('http'):
                    print(f"跳过非HTTP资源: {img_url}")
                    continue
                
                # 跳过小图标
                if any(icon in img_url.lower() for icon in ['logo', 'icon', 'spacer', 'pixel']):
                    print(f"跳过可能的小图标: {img_url}")
                    continue
                
                # 下载图片
                print(f"正在下载 ({i+1}/{len(image_urls)}): {img_url}")
                img_response = requests.get(img_url, headers=headers, timeout=20, stream=True)
                img_response.raise_for_status()
                
                # 检查内容类型
                content_type = img_response.headers.get('Content-Type', '')
                if 'image' not in content_type:
                    print(f"跳过非图片内容 (Content-Type: {content_type}): {img_url}")
                    continue
                
                # 获取文件扩展名
                ext = 'jpg'  # 默认
                if 'jpeg' in content_type:
                    ext = 'jpg'
                elif 'png' in content_type:
                    ext = 'png'
                elif 'gif' in content_type:
                    ext = 'gif'
                elif 'webp' in content_type:
                    ext = 'webp'
                
                # 从URL获取文件名
                filename = os.path.basename(urlparse(img_url).path)
                if not filename or '.' not in filename:
                    filename = f"image_{i+1}.{ext}"
                else:
                    # 清理文件名
                    filename = re.sub(r'[^\w\.-]', '_', filename)
                
                # 完整保存路径
                save_path = os.path.join(save_dir, filename)
                
                # 保存图片
                with open(save_path, 'wb') as f:
                    for chunk in img_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                downloaded += 1
                print(f"已保存: {save_path}")
                
                # 礼貌性延迟
                time.sleep(0.5)
                
            except Exception as e:
                print(f"下载图片失败: {str(e)}")
                continue
                
        print(f"下载完成! 成功下载 {downloaded} 张图片到目录: {save_dir}")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")

# 使用示例
if __name__ == "__main__":
    # 重要提示: 仅用于合法网站和技术研究
    print("图片爬虫 - 修复版")
    print("警告: 仅用于合法网站和技术研究目的")
    
    # 使用一个可靠的示例图片网站
    target_url = "https://unsplash.com/t/nature"  # 免费合法图片网站
    
    # 或者使用您自己的URL (仅限合法内容)
    # target_url = "https://example.com/safe-images"
    
    download_images_from_website(target_url)
