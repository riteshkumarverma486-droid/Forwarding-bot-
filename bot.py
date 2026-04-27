import os
import threading
from pyrogram import Client
from flask import Flask

# Flask app (dummy server for Render)
app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# Telegram Bot
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("❌ Missing ENV variables")

API_ID = int(API_ID)

print("✅ ENV Loaded")

bot = Client(
    "advanced-search-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="handlers")
)

# Run Flask in separate thread
threading.Thread(target=run_web).start()

print("🚀 Bot + Web running...")

bot.run()
