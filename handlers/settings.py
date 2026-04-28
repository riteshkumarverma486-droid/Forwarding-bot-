from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import add_force_channel, remove_force_channel, get_force_channels

ADMINS = [8601554584]

def is_admin(user_id):
    return user_id in ADMINS

@Client.on_message(filters.command("settings"))
async def settings(client, message):
    if not is_admin(message.from_user.id):
        return await message.reply("❌ Not allowed")

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Force Channel", callback_data="add_fc")],
        [InlineKeyboardButton("➖ Remove Force Channel", callback_data="remove_fc")],
        [InlineKeyboardButton("📂 Show Force Channels", callback_data="list_fc")]
    ])

    await message.reply("⚙️ Bot Settings Panel", reply_markup=buttons)
