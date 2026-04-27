from pyrogram import Client, filters
from database import get_connections
from utils.cache import get_cache, set_cache
from config import FORCE_JOIN

@Client.on_message(filters.text & filters.group)
async def search(client, message):
    query = message.text.lower()

    # Force Join check
    if FORCE_JOIN:
        try:
            member = await client.get_chat_member(FORCE_JOIN, message.from_user.id)
            if member.status not in ["member", "administrator", "creator"]:
                return await message.reply(f"⚠️ Join @{FORCE_JOIN} first!")
        except:
            return await message.reply(f"⚠️ Join @{FORCE_JOIN} first!")

    # Cache check
    cached = get_cache(query)
    if cached:
        await cached.copy(message.chat.id)
        return

    channels = get_connections(message.chat.id)

    for (channel_id,) in channels:
        async for msg in client.search_messages(channel_id, query, limit=5):
            if msg.media:
                set_cache(query, msg)
                await msg.copy(message.chat.id)
                return

    await message.reply("❌ No result found")
