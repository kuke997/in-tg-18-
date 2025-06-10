import logging
import os
from telegram import Bot
from telegram.error import TelegramError, InvalidToken

# 配置日志输出
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 从环境变量中读取 Telegram Bot Token 和频道 ID
TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_ID = os.getenv("CHANNEL_USERNAME", "").strip()

logging.info(f"[DEBUG] BOT_TOKEN length: {len(TOKEN)}")
logging.info(f"[DEBUG] CHANNEL_ID: {CHANNEL_ID}")

# 检查 TOKEN 是否有效
if not TOKEN or len(TOKEN.split(":")) != 2:
    logging.error("❌ 无效的 BOT_TOKEN，请检查 GitHub Secrets 中的设置。")
    raise InvalidToken("Invalid BOT_TOKEN format.")

# 初始化 Telegram Bot 实例
bot = Bot(token=TOKEN)

def send_test_images():
    img_urls = [
        "https://picsum.photos/300/200",
        "https://picsum.photos/seed/picsum/300/200"
    ]

    logging.info(f"[测试模式] 准备发送 {len(img_urls)} 张图片")
    for i, url in enumerate(img_urls):
        try:
            bot.send_photo(chat_id=CHANNEL_ID, photo=url, caption=f"测试图片 {i+1}")
            logging.info(f"✅ 成功发送第 {i+1} 张图片")
        except TelegramError as e:
            logging.error(f"❌ 第 {i+1} 张图片发送失败: {e}")

if __name__ == "__main__":
    logging.info("📤 Telegram Bot 测试开始")
    send_test_images()
    logging.info("📤 Telegram Bot 测试结束")
