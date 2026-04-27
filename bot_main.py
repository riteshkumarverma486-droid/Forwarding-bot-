import asyncio
import os
import threading
from flask import Flask
from telethon import TelegramClient, events

# ========== CONFIG ==========
API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH', '')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')

# ========== FLASK APP ==========
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "✅ Bot is running!", 200

# ========== BOT CLIENT ==========
bot = TelegramClient('bot_session', API_ID, API_HASH)

# ========== COMMAND HANDLERS ==========
@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply("""
🚀 **Bot is Alive!**

**Commands:**
/start - Show this menu
/ping - Check bot status
/search <keyword> - Search messages
/connect - Connect channel & group

**Example:** /search hello
""")

@bot.on(events.NewMessage(pattern='/ping'))
async def ping_handler(event):
    await event.reply("🏓 Pong! Bot is working!")

@bot.on(events.NewMessage(pattern='/search(?:$|\\s)'))
async def search_handler(event):
    query = event.raw_text.replace('/search', '').strip()
    if not query:
        await event.reply("❌ Usage: /search <keyword>\n\nExample: /search python")
        return
    await event.reply(f"🔍 Searching for: **{query}**\n\n✅ Search feature is ready! After connecting channels, real results will appear here.")

@bot.on(events.NewMessage(pattern='/connect'))
async def connect_handler(event):
    await event.reply("""
🔗 **How to Connect:**

1. Add bot as **admin** in your channel
2. Add bot to your group
3. Send me the channel username or invite link

**Example:** @my_channel or https://t.me/my_channel
""")

# Echo handler for testing
@bot.on(events.NewMessage)
async def echo_handler(event):
    if not event.message.text.startswith('/') and event.message.text:
        await event.reply(f"📨 Received: {event.message.text[:100]}")

# ========== RUN BOT IN SEPARATE THREAD WITH NEW LOOP ==========
def run_bot():
    """Run Telegram bot in a separate thread with its own event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def start_bot():
        await bot.start(bot_token=BOT_TOKEN)
        print(f"✅ Bot started as: {(await bot.get_me()).username}")
        await bot.run_until_disconnected()
    
    loop.run_until_complete(start_bot())

# ========== MAIN ==========
if __name__ == "__main__":
    print("🤖 Starting Telegram Bot...")
    
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Wait a bit for bot to connect
    import time
    time.sleep(2)
    
    # Start Flask server
    port = int(os.environ.get("PORT", 8080))
    print(f"🔥 Starting web server on port {port}")
    app.run(host="0.0.0.0", port=port)
