import os
import random
import json
import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.error import TelegramError
from apscheduler.schedulers.background import BackgroundScheduler
from crawler import update_cache, CACHE_FILE  # 确保 crawler.py 中定义了这两个

# ---------- 环境变量 & 日志配置 ----------
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_USERNAME")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 打印环境变量状态，帮助调试
logger.info("BOT_TOKEN set: %s", "YES" if TOKEN else "NO")
logger.info("CHANNEL_USERNAME: %s", CHANNEL or "MISSING")

# ---------- 图片缓存加载 ----------
def load_images():
    try:
        with open(CACHE_FILE, 'r') as f:
            imgs = json.load(f)
            logger.info("Loaded %d images from cache", len(imgs))
            return imgs
    except Exception as e:
        logger.warning("Failed to load cache (%s): %s", CACHE_FILE, e)
        return []

# ---------- Bot 命令处理器 ----------
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🔥 Welcome to DesiHotBabeX! 🔥\n"
        "Send /latest to get the latest NSFW pics."
    )

def latest(update: Update, context: CallbackContext):
    imgs = load_images()
    if not imgs:
        update.message.reply_text("Sorry, no images available right now.")
        return
    pic = random.choice(imgs)
    update.message.reply_photo(photo=pic, caption="🔥 Here's a hot Desi pic 🔥")

def keyword_reply(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    for kw in ['hot', 'desi', 'babe', 'nsfw']:
        if kw in text:
            return latest(update, context)
    # 如果不匹配任何关键词，可视需要不回复或提示
    # update.message.reply_text("Send /latest for NSFW pics!")

# ---------- 自动推送功能 ----------
def send_to_channel():
    imgs = load_images()
    if not imgs:
        logger.warning("No images to send in scheduled task.")
        return
    pic = random.choice(imgs)
    bot = Bot(TOKEN)
    try:
        bot.send_photo(chat_id=CHANNEL, photo=pic, caption="🔥 Auto NSFW 🔥")
        logger.info("✅ Sent photo to %s: %s", CHANNEL, pic)
    except TelegramError as e:
        logger.error("❌ Failed to send photo: %s", e.message)

# ---------- 主函数 & 定时任务 ----------
def main():
    # 启动前先更新一次缓存
    update_cache()
    logger.info("Initial cache update complete.")

    # 启动 Bot
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("latest", latest))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, keyword_reply))

    # 定时任务：每2小时更新缓存 & 推送图片
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_cache, 'interval', hours=2, id='cache_update')
    scheduler.add_job(send_to_channel, 'interval', hours=2, id='auto_post')
    scheduler.start()
    logger.info("Scheduler started with jobs: %s", scheduler.get_jobs())

    # 开始监听
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
