import os, random, json, logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from crawler import update_cache, CACHE_FILE

TOKEN = os.getenv('BOT_TOKEN')
CHANNEL = os.getenv('CHANNEL_USERNAME')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_images():
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except:
        return []

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🔥 Welcome! Send /latest for NSFW pics.")

def latest(update: Update, context: CallbackContext):
    imgs = load_images()
    if imgs:
        update.message.reply_photo(photo=random.choice(imgs), caption="🔥 Here's a hot pic 🔥")
    else:
        update.message.reply_text("No images right now. Try later!")

def keyword_reply(update: Update, context: CallbackContext):
    if any(k in update.message.text.lower() for k in ['hot', 'babe', 'desi']):
        latest(update, context)

def send_to_channel():
    bot = Bot(TOKEN)
    imgs = load_images()
    if imgs:
        bot.send_photo(chat_id=CHANNEL, photo=random.choice(imgs), caption="🔥 Auto NSFW 🔥")

def main():
    update_cache()
    send_to_channel()
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("latest", latest))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, keyword_reply))

    from apscheduler.schedulers.blocking import BlockingScheduler
    sched = BlockingScheduler()
    sched.add_job(update_cache, 'interval', hours=2)
    sched.add_job(send_to_channel, 'interval', hours=2)
    sched.start()

