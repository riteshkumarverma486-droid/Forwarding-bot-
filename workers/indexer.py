from pyrogram import Client
from db import add_file
from db import get_connections

async def run_indexer(app: Client):
    # simple periodic scan (on start)
    seen = set()
    for (ch_id,) in set(sum([get_connections(g) for g in []], [])):
        async for msg in app.get_chat_history(ch_id):
            if msg.id in seen: continue
            seen.add(msg.id)
            name = None
            if msg.document: name = msg.document.file_name
            elif msg.video: name = msg.video.file_name
            elif msg.caption: name = msg.caption
            if name:
                add_file(ch_id, msg.id, name)
