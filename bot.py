from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from database import search_movie


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text

    results = search_movie(query)

    if not results:
        return await update.message.reply_text("❌ No results found")

    for text, link in results[:5]:
        keyboard = [[InlineKeyboardButton("📥 Open", url=link)]]

        await update.message.reply_text(
            f"🎬 {text[:100]}...\n🔗 {link}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))

    print("🚀 Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
