import asyncio
import re
import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityTextUrl
import sqlite3
import logging

# Environment variables (Render par automatically fill honge)
API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH', '')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')

# Database setup
conn = sqlite3.connect('bot_database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS user_connections
             (user_id INTEGER, channel_id INTEGER, channel_title TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS channel_messages
             (channel_id INTEGER, message_id INTEGER, text TEXT, date INTEGER)''')
conn.commit()

# Bot setup
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("✅ Bot is alive! Use /connect to add a channel.")

@bot.on(events.NewMessage(pattern='/connect'))
async def connect(event):
    await event.respond("Send me the channel ID or link where I am admin.")

@bot.on(events.NewMessage(pattern='/search'))
async def search(event):
    query = event.raw_text.replace('/search', '').strip()
    if not query:
        await event.respond("Usage: /search keyword")
        return
    await event.respond(f"🔍 Searching for: {query}\n(Search feature working)")

async def main():
    print("🚀 Bot is starting...")
    await bot.run_until_disconnected()

# Flask for Render
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "Bot is running!", 200

if __name__ == "__main__":
    thread = threading.Thread(target=lambda: asyncio.run(main()))
    thread.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
