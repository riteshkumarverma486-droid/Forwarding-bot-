from database import get_force_channels

async def check_join(client, user_id):
    channels = get_force_channels()

    for ch in channels:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False

    return True
