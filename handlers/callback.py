from pyrogram import Client, filters
from utils.force_join import check_join

@Client.on_callback_query(filters.regex("verify_join"))
async def verify_join(client, query):
    user_id = query.from_user.id

    if await check_join(client, user_id):
        await query.message.edit("✅ Verified! Now send your search again 🔍")
    else:
        await query.answer("❌ Join channel first!", show_alert=True)
