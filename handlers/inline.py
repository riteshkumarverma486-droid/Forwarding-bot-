from pyrogram import Client
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent
from db import search_files

@Client.on_inline_query()
async def inline(client, iq):
    q = iq.query.strip().lower()
    if not q:
        return await iq.answer([], cache_time=1)

    results = []
    for ch, mid in search_files(q, limit=10):
        results.append(
            InlineQueryResultArticle(
                title=f"Result: {q}",
                input_message_content=InputTextMessageContent(
                    f"🔎 Result for: {q}\nUse in group to fetch file"
                )
            )
        )
    await iq.answer(results, cache_time=10)
