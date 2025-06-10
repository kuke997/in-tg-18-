import logging
import os
import json
from telegram import Bot
from telegram.error import TelegramError, InvalidToken

# 配置日志输出
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 读取环境变量
TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_ID = os.getenv("CHANNEL_USERNAME", "").strip()

logging.info(f"[DEBUG] BOT_TOKEN length: {len(TOKEN)}")
logging.info(f"[DEBUG] CHANNEL_ID: {CHANNEL_ID}")

if not TOKEN or len(TOKEN.split(":")) != 2:
    logging.error("❌ 无效的 BOT_TOKEN，请检查 GitHub Secrets 中的设置。")
    raise InvalidToken("Invalid BOT_TOKEN format.")

bot = Bot(token=TOKEN)

CACHE_FILE = 'img_cache.json'

def send_to_channel():
    """
    从缓存文件读取图片链接，发送到 Telegram 频道
    """
    if not os.path.exists(CACHE_FILE):
        logging.error(f"缓存文件 {CACHE_FILE} 不存在，无法发送图片。")
        return

    with open(CACHE_FILE, 'r') as f:
        img_urls = json.load(f)

    logging.info(f"准备发送 {len(img_urls)} 张图片到频道 {CHANNEL_ID}")

    for i, url in enumerate(img_urls):
        try:
            bot.send_photo(chat_id=CHANNEL_ID, photo=url, caption=f"自动推送图片 {i+1}")
            logging.info(f"✅ 成功发送第 {i+1} 张图片")
        except TelegramError as e:
            logging.error(f"❌ 第 {i+1} 张图片发送失败: {e}")

def send_test_images():
    img_urls = [
        "https://picsum.photos/300/200",
        "https://picsum.photos/seed/picsum/300/200"
    ]

    logging.info(f"[测试模式] 准备发送 {len(img_urls)} 张测试图片")
    for i, url in enumerate(img_urls):
        try:
            bot.send_photo(chat_id=CHANNEL_ID, photo=url, caption=f"测试图片 {i+1}")
            logging.info(f"✅ 成功发送第 {i+1} 张测试图片")
        except TelegramError as e:
            logging.error(f"❌ 第 {i+1} 张测试图片发送失败: {e}")

if __name__ == "__main__":
    logging.info("📤 Telegram Bot 测试开始")
    send_test_images()
    logging.info("📤 Telegram Bot 测试结束")
