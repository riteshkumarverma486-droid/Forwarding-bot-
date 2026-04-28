from pyrogram import Client, filters
from db import add_connection

@Client.on_message(filters.command("connect") & filters.group)
async def connect(client, m):
    try:
        if m.reply_to_message:
            ch_id = m.reply_to_message.forward_from_chat.id
        else:
            ch_id = int(m.command[1])
        add_connection(m.from_user.id, m.chat.id, ch_id)
        await m.reply("✅ Channel connected")
    except:
        await m.reply("❌ Use:\n/connect -100channelid or reply to a channel post")
import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()
