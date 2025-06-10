import os
import time
import requests
import re
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent

def get_random_headers():
    """生成随机的浏览器头信息"""
    ua = UserAgent()
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "TE": "Trailers",
    }

def download_images_from_website(url, save_dir="downloaded_images"):
    """
    高级图片爬虫 - 绕过反爬机制版
    
    参数:
    url (str): 目标网站URL
    save_dir (str): 图片保存目录
    """
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    
    # 创建会话并设置随机头信息
    session = requests.Session()
    headers = get_random_headers()
    headers["Referer"] = url
    
    try:
        print(f"正在访问: {url}")
        
        # 首次访问获取cookies
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        print(f"状态码: {response.status_code}")
        
        # 检查robots.txt
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        try:
            robots_response = session.get(robots_url, headers=headers, timeout=5)
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
            for attr in ['src', 'data-src', 'data-original', 'data-srcset', 'data-image', 'srcset']:
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
                delay = random.uniform(1.0, 3.0)
                time.sleep(delay)
                
                # 更新头信息
                headers = get_random_headers()
                headers["Referer"] = url
                
                # 下载图片
                print(f"正在下载 ({i+1}/{len(valid_urls)}): {img_url}")
                img_response = session.get(img_url, headers=headers, timeout=20, stream=True)
                
                # 检查状态码
                if img_response.status_code != 200:
                    print(f"跳过，状态码 {img_response.status_code}: {img_url}")
                    continue
                
                # 检查内容类型
                content_type = img_response.headers.get('Content-Type', '')
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
                
                # 从URL获取文件名
                filename = os.path.basename(urlparse(img_url).path)
                if not filename or '.' not in filename:
                    filename = f"image_{i+1}.{ext}"
                else:
                    # 清理文件名
                    filename = re.sub(r'[^\w\.-]', '_', filename)
                    # 确保有扩展名
                    if '.' not in filename:
                        filename += f".{ext}"
                
                # 完整保存路径
                save_path = os.path.join(save_dir, filename)
                
                # 避免覆盖
                counter = 1
                while os.path.exists(save_path):
                    base, ext = os.path.splitext(filename)
                    save_path = os.path.join(save_dir, f"{base}_{counter}{ext}")
                    counter += 1
                
                # 保存图片
                with open(save_path, 'wb') as f:
                    for chunk in img_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
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
    # 安装必要库: pip install fake-useragent
    
    print("高级图片爬虫 - 绕过反爬机制版")
    print("警告: 仅用于合法网站和技术研究目的")
    
    # 使用对爬虫友好的图片网站
    target_url = "https://www.istockphoto.com/photos/nature"  # 大型图库网站
    
    # 或者使用其他备选网站:
    # target_url = "https://www.gettyimages.com/photos/nature"
    # target_url = "https://pixabay.com/images/search/nature/"
    
    # 如果仍然不行，尝试更简单的网站:
    # target_url = "https://picsum.photos/"  # 最简单的图片API
    
    downloaded_count = download_images_from_website(target_url)
    
    if downloaded_count == 0:
        print("\n如果仍然无法下载图片，可能原因:")
        print("1. 网站有强大的反爬机制")
        print("2. 图片是动态加载的（需要Selenium）")
        print("3. 需要处理JavaScript渲染的内容")
        print("4. IP地址可能被暂时封锁")
        
        print("\n解决方案建议:")
        print("1. 使用Selenium模拟浏览器: pip install selenium webdriver-manager")
        print("2. 使用代理服务器")
        print("3. 增加延迟时间和随机化请求模式")
        print("4. 尝试不同的目标网站")
