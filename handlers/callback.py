from pyrogram import Client, filters
from utils.force_join import is_joined_all

@Client.on_callback_query(filters.regex("verify_join"))
async def verify(client, q):
    if await is_joined_all(client, q.from_user.id):
        await q.message.edit("✅ Verified! Ab search karo 🔍")
    else:
        await q.answer("❌ Pehle sab channels join karo", show_alert=True)
