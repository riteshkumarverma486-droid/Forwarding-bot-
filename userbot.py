from telethon import TelegramClient
from config import API_ID, API_HASH
from database import save_movie

client = TelegramClient("session", API_ID, API_HASH)

channels = []  # add channels manually or from DB later


async def index_channels():
    await client.start()

    for ch in channels:
        async for msg in client.iter_messages(ch, limit=100):
            if msg.text:
                link = f"https://t.me/{ch}/{msg.id}"
                save_movie(msg.text, link)

    print("✅ Indexing complete")


with client:
    client.loop.run_until_complete(index_channels())
