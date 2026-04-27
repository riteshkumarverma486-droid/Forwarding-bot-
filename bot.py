import os
from pyrogram import Client

try:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    print("✅ ENV Loaded")

    app = Client(
        "advanced-search-bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="handlers")
    )

    print("🚀 Bot Starting...")

    app.run()

except Exception as e:
    print(f"❌ ERROR: {e}")
