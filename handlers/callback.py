from database import add_force_channel, remove_force_channel, get_force_channels

@Client.on_callback_query()
async def cb_handler(client, query):
    data = query.data

    if data == "add_fc":
        await query.message.reply("Send channel username (without @)")
    
    elif data == "remove_fc":
        await query.message.reply("Send channel username to remove")

    elif data == "list_fc":
        channels = get_force_channels()
        text = "📂 Force Channels:\n\n"
        for ch in channels:
            text += f"@{ch}\n"
        await query.message.reply(text)
