import logging
import os
from telegram import Bot
from telegram.error import TelegramError

# 配置日志输出
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Telegram 配置（使用环境变量或直接写入也可）
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "你的_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@你的频道ID")  # 注意带 @

bot = Bot(token=TOKEN)

def send_test_images():
    # 模拟的图片链接
    img_urls = [
        "https://picsum.photos/300/200",
        "https://picsum.photos/seed/picsum/300/200"
    ]

    logging.info(f"[测试模式] 模拟生成图片链接 {len(img_urls)} 条")
    for i, url in enumerate(img_urls):
        logging.info(f"[测试模式] 第 {i+1} 条图片链接: {url}")
        try:
            bot.send_photo(chat_id=CHANNEL_ID, photo=url, caption=f"测试图片 {i+1}")
            logging.info(f"✅ 成功发送第 {i+1} 张图片")
        except TelegramError as e:
            logging.error(f"❌ 发送图片失败: {e}")

if __name__ == "__main__":
    logging.info("📤 Telegram Bot 测试开始")
    send_test_images()
    logging.info("📤 Telegram Bot 测试结束")
