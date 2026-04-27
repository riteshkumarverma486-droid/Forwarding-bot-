from pyrogram import Client, filters
from database import add_connection

@Client.on_message(filters.command("connect") & filters.group)
async def connect(client, message):
    try:
        user_id = message.from_user.id
        group_id = message.chat.id

        if message.reply_to_message:
            channel_id = message.reply_to_message.forward_from_chat.id
        else:
            channel_id = int(message.command[1])

        add_connection(user_id, group_id, channel_id)

        await message.reply("✅ Channel connected successfully!")

    except:
        await message.reply("❌ Use:\n/connect -100channelid OR reply to channel post")
