from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply(
        "👋 Welcome!\n\n"
        "Use /connect to link your channel & group\n"
        "Then just type anything in group to search 🔍"
    )
