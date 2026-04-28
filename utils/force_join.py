from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import FORCE_JOIN

def channels():
    return [c.strip().replace("@","") for c in FORCE_JOIN.split(",") if c.strip()]

async def is_joined_all(client, user_id):
    for ch in channels():
        try:
            m = await client.get_chat_member(ch, user_id)
            if m.status not in ["member", "administrator", "creator"]:
                return False
        except Exception as e:
            print("Join check error:", e)
            return False
    return True

def join_kb():
    btns = []
    for ch in channels():
        btns.append([InlineKeyboardButton(f"🔗 Join @{ch}", url=f"https://t.me/{ch}")])
    btns.append([InlineKeyboardButton("✅ Verify", callback_data="verify_join")])
    return InlineKeyboardMarkup(btns)
