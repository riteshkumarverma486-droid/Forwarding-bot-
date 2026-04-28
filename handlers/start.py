from pyrogram import Client, filters

@Client.on_message(filters.command("start"))
async def start(_, m):
    await m.reply("👋 Welcome!\nGroup me search karo 🔍")
