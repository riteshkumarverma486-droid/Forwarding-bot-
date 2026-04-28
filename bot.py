import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
# from workers.indexer import run_indexer  # optional

app = Client(
    "ultimate-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="handlers")
)

async def main():
    await app.start()
    print("🚀 Bot started")
    # await run_indexer(app)  # optional first run indexing
    await idle()

from pyrogram import idle

if __name__ == "__main__":
    asyncio.run(main())
