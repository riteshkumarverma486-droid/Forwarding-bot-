from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import FORCE_JOIN

async def check_join(client, user_id):
    channel = FORCE_JOIN.replace("@", "")

    try:
        member = await client.get_chat_member(channel, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print("Join Error:", e)
        return False


def join_button():
    channel = FORCE_JOIN.replace("@", "")

    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔗 Join Channel", url=f"https://t.me/{channel}")],
            [InlineKeyboardButton("✅ Verify", callback_data="verify_join")]
        ]
    )
