from pyrogram import Client, filters
from database import add_connection

@Client.on_message(filters.command("connect"))
async def connect(client, message):
    try:
        user_id = message.from_user.id
        group_id = message.chat.id

        # Example: /connect -1001234567890
        channel_id = int(message.command[1])

        add_connection(user_id, group_id, channel_id)

        await message.reply("✅ Channel connected successfully!")

    except:
        await message.reply("❌ Usage: /connect -100channelid")
