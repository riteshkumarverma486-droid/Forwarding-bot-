from pyrogram import Client, filters
from utils.force_join import check_join, join_button
from database import get_connections
from utils.cache import get_cache, set_cache

@Client.on_message(filters.text & filters.group)
async def search(client, message):
    query = message.text.lower()

    # 🔐 Force Join Check
    if not await check_join(client, message.from_user.id):
        return await message.reply(
            "⚠️ Please join our channel first to use the bot",
            reply_markup=join_button()
        )

    # ⚡ Cache check
    cached = get_cache(query)
    if cached:
        await cached.copy(message.chat.id)
        return

    channels = get_connections(message.chat.id)

    for (channel_id,) in channels:
        async for msg in client.search_messages(channel_id, query, limit=5):
            if msg.text or msg.caption or msg.media:
                set_cache(query, msg)
                await msg.copy(message.chat.id)
                return

    await message.reply("❌ No result found")
