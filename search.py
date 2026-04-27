@Client.on_message(filters.text & filters.group)
async def search(client, message):
    query = message.text.lower()

    print("Searching for:", query)

    channels = get_connections(message.chat.id)

    for (channel_id,) in channels:
        async for msg in client.search_messages(channel_id, query, limit=5):
            if msg.text or msg.caption:
                await msg.copy(message.chat.id)
                return

    await message.reply("❌ No result found")
