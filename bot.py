import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, ADMINS

DB_FILE = "database.json"

# Load DB
def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"channels": []}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Movie Search Bot Active\n\nSend movie name to search."
    )

# Add channel
async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return
    
    db = load_db()
    channel = context.args[0]

    if channel not in db["channels"]:
        db["channels"].append(channel)
        save_db(db)
        await update.message.reply_text(f"✅ Channel added: {channel}")
    else:
        await update.message.reply_text("Already exists.")

# Remove channel
async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return
    
    db = load_db()
    channel = context.args[0]

    if channel in db["channels"]:
        db["channels"].remove(channel)
        save_db(db)
        await update.message.reply_text(f"❌ Removed: {channel}")
    else:
        await update.message.reply_text("Not found.")

# List channels
async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    channels = "\n".join(db["channels"]) or "No channels added"
    await update.message.reply_text(f"📡 Channels:\n{channels}")

# Search system (basic simulation)
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    db = load_db()

    if not db["channels"]:
        await update.message.reply_text("❌ No channels configured.")
        return

    results = []

    # ⚠️ Telegram bots cannot directly read messages from channels
    # So this is simulated format
    for ch in db["channels"]:
        results.append(f"🎬 {query}\n📡 Source: {ch}\n🔗 https://t.me/{ch}")

    if results:
        for r in results[:5]:
            keyboard = [[InlineKeyboardButton("Open Channel", url=r.split("\n")[-1].split(" ")[-1])]]
            await update.message.reply_text(r, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("❌ No results found.")

# Main
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_channel))
    app.add_handler(CommandHandler("remove", remove_channel))
    app.add_handler(CommandHandler("list", list_channels))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
