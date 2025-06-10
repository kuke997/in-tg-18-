import os
import json
import logging
from telegram import Bot
from telegram.error import TelegramError, InvalidToken

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = os.getenv('BOT_TOKEN', '').strip()
CHANNEL_ID = os.getenv('CHANNEL_USERNAME', '').strip()

logging.info(f"BOT_TOKEN length: {len(TOKEN)}")
logging.info(f"CHANNEL_ID: {CHANNEL_ID}")

if not TOKEN or len(TOKEN.split(':')) != 2:
    logging.error("Invalid BOT_TOKEN format!")
    raise InvalidToken("Invalid BOT_TOKEN format")

bot = Bot(token=TOKEN)

CACHE_FILE = 'img_cache.json'

def send_to_channel():
    if not os.path.exists(CACHE_FILE):
        logging.error(f"Cache file {CACHE_FILE} does not exist!")
        return

    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        img_urls = json.load(f)

    logging.info(f"Sending {len(img_urls)} images to channel {CHANNEL_ID}")

    for idx, url in enumerate(img_urls, 1):
        try:
            bot.send_photo(chat_id=CHANNEL_ID, photo=url, caption=f"自动推送图片 {idx}")
            logging.info(f"Sent image {idx} successfully")
        except TelegramError as e:
            logging.error(f"Failed to send image {idx}: {e}")

if __name__ == "__main__":
    send_to_channel()
