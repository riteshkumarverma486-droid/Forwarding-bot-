@Client.on_message(filters.text & filters.private)
async def manage_channels(client, message):
    user_id = message.from_user.id

    if user_id not in ADMINS:
        return

    text = message.text.replace("@", "")

    if "add" in message.text.lower():
        add_force_channel(text)
        await message.reply(f"✅ Added @{text}")

    elif "remove" in message.text.lower():
        remove_force_channel(text)
        await message.reply(f"❌ Removed @{text}")
