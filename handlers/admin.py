from pyrogram import Client, filters
from config import ADMINS
from db import conn, cur

def is_admin(uid): return uid in ADMINS

@Client.on_message(filters.command("stats"))
async def stats(client, m):
    if not is_admin(m.from_user.id): return
    cur.execute("SELECT COUNT(*) FROM files")
    files = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT group_id) FROM connections")
    groups = cur.fetchone()[0]
    await m.reply(f"📊 Files: {files}\n👥 Groups: {groups}")
ADMINS = [8601554584]  # apna telegram id

def is_admin(user_id):
    return user_id in ADMINS
