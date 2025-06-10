import os
import random
import json
import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.error import TelegramError
from apscheduler.schedulers.background import BackgroundScheduler
from crawler import update_cache, CACHE_FILE

# 环境变量 & 日志
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_USERNAME")

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载缓存
def load_images():
    try:
        imgs = json.load(open(CACHE_FILE, 'r'))
        logger.info("Loaded %d images from cache", len(imgs))
        return imgs
    except Exception as e:
        logger.warning("Failed to load cache: %s", e)
        return []

# /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🔥 DesiHotBabeX Bot 🔥\nSend /latest to get a hot pic!")

# /latest
def latest(update: Update, context: CallbackContext):
    imgs = load_images()
    if not imgs:
        update.message.reply_text("No images right now. Try later.")
        return
    pic = random.choice(imgs)
    update.message.reply_photo(photo=pic, caption="🔥 Here's a hot Desi pic 🔥")

# 关键词触发
def keyword_reply(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    if any(k in text for k in ['hot','desi','babe','nsfw']):
        latest(update, context)

# 定时推送
def send_to_channel():
    imgs = load_images()
    if not imgs:
        logger.warning("No images to send on schedule")
        return
    pic = random.choice(imgs)
    bot = Bot(TOKEN)
    try:
        bot.send_photo(chat_id=CHANNEL, photo=pic, caption="🔥 Auto NSFW 🔥")
        logger.info("Sent scheduled photo: %s", pic)
    except TelegramError as e:
        logger.error("Failed scheduled send: %s", e)

# 主入口
def main():
    # 首次更新缓存
    update_cache()

    # 启动 Bot
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("latest", latest))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, keyword_reply))

    # 定时任务
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_cache, 'interval', hours=2, id='cache_upd')
    scheduler.add_job(send_to_channel, 'interval', hours=2, id='auto_post')
    scheduler.start()
    logger.info("Scheduler started: %s", scheduler.get_jobs())

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
