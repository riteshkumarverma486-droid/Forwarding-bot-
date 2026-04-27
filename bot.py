import asyncio
import os
from telethon import TelegramClient, events
from flask import Flask

# ========== CONFIG ==========
API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH', '')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')

print(f"🔑 API_ID: {API_ID}")
print(f"🔑 BOT_TOKEN length: {len(BOT_TOKEN) if BOT_TOKEN else 0}")

# ========== FLASK ==========
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "✅ Bot Running", 200

# ========== BOT ==========
bot = TelegramClient('bot_session', API_ID, API_HASH)

# Command handlers
@bot.on(events.NewMessage(pattern='/start'))
async def start_cmd(event):
    await event.reply("✅ Bot is alive!\n\nSend /ping to test")

@bot.on(events.NewMessage(pattern='/ping'))
async def ping_cmd(event):
    await event.reply("🏓 Pong! Bot is working.")

@bot.on(events.NewMessage(pattern='/reindex'))
async def reindex_cmd(event):
    await event.reply("🔄 Reindex command received. (Feature coming soon)")

@bot.on(events.NewMessage(pattern='/search'))
async def search_cmd(event):
    query = event.raw_text.replace('/search', '').strip()
    if not query:
        await event.reply("Usage: /search <keyword>")
    else:
        await event.reply(f"🔍 Searching for: {query}")

@bot.on(events.NewMessage)
async def echo_cmd(event):
    # Reply to any non-command message
    if not event.message.text.startswith('/'):
        await event.reply(f"📨 You said: {event.message.text[:100]}")

# ========== MAIN ==========
async def main():
    print("🤖 Starting bot...")
    await bot.start(bot_token=BOT_TOKEN)
    me = await bot.get_me()
    print(f"✅ Bot started as: @{me.username}")
    print(f"✅ Bot ID: {me.id}")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    import threading
    
    # Run bot in thread with new event loop
    def run_bot():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask
    port = int(os.environ.get("PORT", 8080))
    print(f"🔥 Web server on port {port}")
    app.run(host="0.0.0.0", port=port)
