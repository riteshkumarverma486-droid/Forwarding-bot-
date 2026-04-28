from pyrogram import Client, filters
from utils.force_join import is_joined_all, join_kb
from db import get_connections, search_files
from utils.cache import get_cache, set_cache

@Client.on_message(filters.text & filters.group)
async def search(client, m):
    q = m.text.strip().lower()

    if not await is_joined_all(client, m.from_user.id):
        return await m.reply("⚠️ Use karne ke liye join karein", reply_markup=join_kb())

    # cache
    c = get_cache(q)
    if c:
        ch, mid = c
        return await client.copy_message(m.chat.id, ch, mid)

    # DB search (fast)
    rows = search_files(q, limit=5)
    if rows:
        ch, mid = rows[0]
        set_cache(q, (ch, mid))
        return await client.copy_message(m.chat.id, ch, mid)

    # fallback: live search in connected channels
    for (ch_id,) in get_connections(m.chat.id):
        async for msg in client.search_messages(ch_id, q, limit=5):
            if msg.text or msg.caption or msg.media:
                set_cache(q, (ch_id, msg.id))
                return await msg.copy(m.chat.id)

    await m.reply("❌ No result found")
