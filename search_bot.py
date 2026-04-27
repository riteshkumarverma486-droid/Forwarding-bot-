import asyncio
import os
from flask import Flask
from telethon import TelegramClient, events

# ========== CONFIG ==========
API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH', '')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')

print(f"📡 Starting bot with API_ID: {API_ID}")

# ========== FLASK APP ==========
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "✅ Bot Running", 200

# ========== CREATE BOT CLIENT ==========
bot = TelegramClient('bot_session', API_ID, API_HASH)

# ========== COMMAND HANDLERS ==========
@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply("✅ Bot is alive!\n\nSend /ping to test")

@bot.on(events.NewMessage(pattern='/ping'))
async def ping_handler(event):
    await event.reply("🏓 Pong! Bot is working.")

@bot.on(events.NewMessage(pattern='/reindex'))
async def reindex_handler(event):
    await event.reply("🔄 Reindex command received.")

@bot.on(events.NewMessage(pattern='/search'))
async def search_handler(event):
    query = event.raw_text.replace('/search', '').strip()
    if not query:
        await event.reply("Usage: /search <keyword>")
    else:
        await event.reply(f"🔍 Searching for: {query}")

@bot.on(events.NewMessage)
async def echo_handler(event):
    if event.message.text and not event.message.text.startswith('/'):
        await event.reply(f"📨 {event.message.text[:100]}")

# ========== MAIN FUNCTION ==========
async def main():
    print("🤖 Starting bot...")
    await bot.start(bot_token=BOT_TOKEN)
    me = await bot.get_me()
    print(f"✅ Bot started as: @{me.username}")
    print("✅ Bot is now listening for commands...")
    await bot.run_until_disconnected()

# ========== RUN ==========
if __name__ == "__main__":
    import threading
    
    # Create new event loop for bot
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Run bot in main thread's loop
    def run_bot():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    
    # Start bot thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask in main thread
    port = int(os.environ.get("PORT", 8080))
    print(f"🔥 Web server on port {port}")
    app.run(host="0.0.0.0", port=port)
