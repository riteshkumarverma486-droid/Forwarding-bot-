import asyncio
from datetime import datetime
import logging
from telethon import TelegramClient, events, Button
from telethon.tl.types import MessageEntityTextUrl
from telethon.errors import FloodWaitError
import re

from config import API_ID, API_HASH, BOT_TOKEN, SEARCH_LIMIT, MAX_SEARCH_PER_MINUTE, ADMIN_IDS
from database import Database
from message_indexer import MessageIndexer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize
db = Database()
bot = TelegramClient('forwarding_bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
indexer = MessageIndexer(bot, db)

# Track user states for multi-step operations
user_states = {}

# ============ HELPER FUNCTIONS ============

async def send_formatted_response(event, results, query, channel_id=None):
    """Send search results in nice format"""
    if not results:
        await event.reply(f"❌ No results found for **{query}**\n\nTry different keywords or /reindex")
        return
    
    # Build response message
    response = f"🔍 **Search Results for: {query}**\n"
    response += f"📊 Found {len(results)} messages\n\n"
    
    for idx, (ch_id, msg_id, text, date, media_type) in enumerate(results[:10], 1):
        # Truncate long text
        preview = text[:200] + "..." if len(text) > 200 else text
        preview = preview.replace('\n', ' ').strip()
        
        # Get channel name from database
        user_id = event.sender_id
        connections = db.get_user_connections(user_id)
        channel_name = next((conn[1] for conn in connections if conn[0] == ch_id), "Unknown")
        
        # Format date
        date_str = date.strftime("%d %b %Y, %H:%M")
        
        # Media indicator
        media_icon = ""
        if media_type == 'photo':
            media_icon = "🖼️ "
        elif media_type == 'video':
            media_icon = "🎥 "
        elif media_type == 'document':
            media_icon = "📎 "
        
        # Create message link
        # Note: For private channels, use different format
        msg_link = f"https://t.me/c/{str(ch_id)[4:]}/{msg_id}"
        
        response += f"{idx}. {media_icon}[{channel_name}]({msg_link})\n"
        response += f"   📅 {date_str}\n"
        response += f"   💬 {preview}\n\n"
    
    if len(results) > 10:
        response += f"_And {len(results)-10} more results..._\n"
    
    response += f"\n💡 Use /next to see more results"
    
    # Send as reply
    await event.reply(response, link_preview=False)

# ============ COMMAND HANDLERS ============

@bot.on(events.NewMessage(pattern='/(start|help)'))
async def start_handler(event):
    """Handle /start and /help commands"""
    user_id = event.sender_id
    
    welcome_text = """
🚀 **Professional Forwarding Bot v3.0**

**Features:**
• 📚 Connect channels as message database
• 🔍 Search across connected channels instantly
• ⚡ Auto-index new messages in real-time
• 📊 Smart caching for fast search
• 🛡️ Rate limiting protection

**How to Use:**
1. `/connect` - Connect channel + group
2. `/search <keyword>` - Search messages
3. `/stats` - View your usage stats
4. `/channels` - Manage your connections
5. `/reindex` - Refresh message cache

**Example Search:**
`/search Python programming`

**Need Help?** Send /tutorial for detailed guide
"""
    
    # Create buttons
    buttons = [
        [Button.inline("➕ Connect Channel", b"connect"),
         Button.inline("🔍 Search", b"search")],
        [Button.inline("📊 My Stats", b"stats"),
         Button.inline("📚 Tutorial", b"tutorial")]
    ]
    
    await event.respond(welcome_text, buttons=buttons)
    logger.info(f"User {user_id} started the bot")

@bot.on(events.NewMessage(pattern='/connect'))
async def connect_handler(event):
    """Handle /connect command - interactive setup"""
    user_id = event.sender_id
    
    # Get user's channels
    dialogs = await bot.get_dialogs()
    channels = [d for d in dialogs if d.is_channel]
    groups = [d for d in dialogs if d.is_group]
    
    if not channels:
        await event.reply("❌ No channels found!\n\nMake sure bot is added as admin in a channel and invite it to chat.")
        return
    
    # Show channel selection
    user_states[user_id] = {'step': 'selecting_channel'}
    
    buttons = []
    for channel in channels[:20]:  # Limit to 20 channels
        buttons.append([Button.inline(f"📢 {channel.title[:25]}", f"ch_{channel.id}".encode())])
    
    buttons.append([Button.inline("❌ Cancel", b"cancel")])
    
    await event.respond(
        "🔗 **Step 1/2: Select Channel**\n\n"
        "Choose the channel you want to use as message database:\n"
        f"Found {len(channels)} channels",
        buttons=buttons
    )

@bot.on(events.NewMessage(pattern='/search(?:$|\\s)'))
async def search_handler(event):
    """Handle /search <query> command"""
    user_id = event.sender_id
    
    # Rate limiting check
    if not db.check_rate_limit(user_id, MAX_SEARCH_PER_MINUTE):
        await event.reply("⏳ **Rate limit exceeded!**\n\nPlease wait 1 minute before searching again.")
        return
    
    # Extract query
    query = event.raw_text.replace('/search', '').strip()
    
    if not query:
        await event.reply("❌ **Please provide search query**\n\nExample: `/search hello world`")
        return
    
    # Get user's connected channels
    connections = db.get_user_connections(user_id)
    
    if not connections:
        await event.reply(
            "❌ **No channels connected!**\n\n"
            "Use /connect to add a channel and group first.\n\n"
            "**Why connect both?**\n"
            "• Channel = Message database\n"
            "• Group = Where search results will be sent"
        )
        return
    
    # Send processing status
    status_msg = await event.reply(f"🔍 Searching for **{query}**...\n📚 Checking {len(connections)} channels")
    
    # Perform search
    channel_ids = [conn[0] for conn in connections]
    results = db.search_messages(channel_ids, query, SEARCH_LIMIT)
    
    # Log the search
    db.log_search(user_id, query, len(results))
    
    await status_msg.delete()
    
    # Send results
    await send_formatted_response(event, results, query)
    
    logger.info(f"User {user_id} searched '{query}': {len(results)} results")

@bot.on(events.NewMessage(pattern='/channels'))
async def channels_handler(event):
    """List connected channels and groups"""
    user_id = event.sender_id
    connections = db.get_user_connections(user_id)
    
    if not connections:
        await event.reply("📭 **No connections found**\n\nUse /connect to add channels")
        return
    
    response = f"📚 **Your Connections ({len(connections)})**\n\n"
    
    for idx, (ch_id, ch_title, grp_id, grp_title) in enumerate(connections, 1):
        # Count indexed messages
        response += f"**{idx}. {ch_title}**\n"
        response += f"   📌 Channel ID: `{ch_id}`\n"
        response += f"   👥 Group: {grp_title}\n"
        response += f"   🔗 [Open Channel](https://t.me/c/{str(ch_id)[4:]})\n\n"
    
    buttons = [[Button.inline("➕ Add Connection", b"connect"), 
                Button.inline("🗑 Remove", b"disconnect")]]
    
    await event.respond(response, buttons=buttons, link_preview=False)

@bot.on(events.NewMessage(pattern='/stats'))
async def stats_handler(event):
    """Show user statistics"""
    user_id = event.sender_id
    
    # Get recent searches
    recent = db.get_recent_searches(user_id, 5)
    
    if not recent:
        await event.reply("📊 **No search history yet**\n\nStart searching with /search <keyword>")
        return
    
    response = f"📊 **Your Search Statistics**\n\n"
    response += f"🕐 **Recent Searches:**\n"
    
    for query, count, time in recent:
        time_str = time.strftime("%d %b, %H:%M")
        response += f"• {query} - {count} results ({time_str})\n"
    
    await event.respond(response)

@bot.on(events.NewMessage(pattern='/reindex'))
async def reindex_handler(event):
    """Manually reindex all connected channels"""
    user_id = event.sender_id
    connections = db.get_user_connections(user_id)
    
    if not connections:
        await event.reply("❌ No channels connected!")
        return
    
    status_msg = await event.reply("🔄 **Reindexing started...**\nThis may take a few minutes.")
    
    total_indexed = 0
    for channel_id, channel_title, _, _ in connections:
        await status_msg.edit(f"📚 Indexing: {channel_title}...")
        result = await indexer.index_channel(channel_id, limit=2000)
        if result['status'] == 'success':
            total_indexed += result.get('indexed', 0)
        await asyncio.sleep(2)  # Rate limit protection
    
    await status_msg.edit(
        f"✅ **Reindexing Complete!**\n\n"
        f"📊 Total messages indexed: {total_indexed}\n"
        f"📚 Channels processed: {len(connections)}"
    )

@bot.on(events.NewMessage(pattern='/disconnect'))
async def disconnect_handler(event):
    """Disconnect channel"""
    user_id = event.sender_id
    connections = db.get_user_connections(user_id)
    
    if not connections:
        await event.reply("❌ No connections to remove!")
        return
    
    buttons = []
    for channel_id, channel_title, _, _ in connections[:10]:
        buttons.append([Button.inline(f"❌ {channel_title[:25]}", f"disconnect_{channel_id}".encode())])
    
    buttons.append([Button.inline("❌ Cancel", b"cancel")])
    
    await event.reply("🗑 **Select channel to disconnect:**", buttons=buttons)

# ============ CALLBACK HANDLERS ============

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    """Handle button callbacks"""
    user_id = event.sender_id
    data = event.data.decode()
    
    if data.startswith('ch_'):
        # Channel selected
        channel_id = int(data.split('_')[1])
        
        # Get groups
        dialogs = await bot.get_dialogs()
        groups = [d for d in dialogs if d.is_group]
        
        if not groups:
            await event.edit("❌ No groups found!\n\nAdd bot to a group first.")
            return
        
        user_states[user_id] = {'step': 'selecting_group', 'channel_id': channel_id}
        
        buttons = []
        for group in groups[:20]:
            buttons.append([Button.inline(f"👥 {group.title[:25]}", f"grp_{group.id}".encode())])
        
        buttons.append([Button.inline("❌ Cancel", b"cancel")])
        
        await event.edit(
            "🔗 **Step 2/2: Select Group**\n\n"
            "Choose where search results should be sent:",
            buttons=buttons
        )
    
    elif data.startswith('grp_'):
        # Group selected, complete connection
        group_id = int(data.split('_')[1])
        channel_id = user_states.get(user_id, {}).get('channel_id')
        
        if not channel_id:
            await event.edit("❌ Session expired! Please start again with /connect")
            return
        
        # Get entities
        channel = await bot.get_entity(channel_id)
        group = await bot.get_entity(group_id)
        
        # Save to database
        db.add_connection(user_id, channel_id, channel.title, group_id, group.title)
        
        # Start indexing in background
        asyncio.create_task(indexer.index_channel(channel_id))
        
        await event.edit(
            f"✅ **Connection complete!**\n\n"
            f"📢 Channel: {channel.title}\n"
            f"👥 Group: {group.title}\n\n"
            f"🔍 Bot is now indexing messages...\n"
            f"You can search using /search <keyword>"
        )
        
        # Clean up user state
        if user_id in user_states:
            del user_states[user_id]
    
    elif data.startswith('disconnect_'):
        channel_id = int(data.split('_')[1])
        db.remove_connection(user_id, channel_id)
        await event.edit(f"✅ **Disconnected!**\n\nChannel removed from your connections.")
    
    elif data == "connect":
        await connect_handler(event)
    
    elif data == "search":
        await event.respond("🔍 **Enter your search query:**\nExample: hello world")
    
    elif data == "stats":
        await stats_handler(event)
    
    elif data == "tutorial":
        tutorial = """
📚 **Tutorial - How to Use Forwarding Bot**

**Step 1: Connect**
1. Add bot as admin in your channel
2. Add bot to your group
3. Run /connect and select both

**Step 2: Index**
Bot will automatically index channel messages

**Step 3: Search**
Use /search <keyword> in the group

**Pro Tips:**
• Use quotes for exact match: /search "hello world"
• Try different keywords for better results
• Use /reindex to refresh cache
"""
        await event.edit(tutorial)
    
    elif data == "cancel":
        await event.edit("❌ Operation cancelled.")
    
    await event.answer()

# ============ AUTO-INDEX NEW MESSAGES ============

@bot.on(events.NewMessage)
async def auto_index(event):
    """Auto-index new messages from connected channels"""
    if event.is_channel and event.message.text:
        chat_id = event.chat_id
        
        # Check if this channel is connected by any user
        connections = db.get_user_connections_by_channel(chat_id) if hasattr(db, 'get_user_connections_by_channel') else []
        
        if connections:
            db.cache_message(
                chat_id,
                event.message.id,
                event.message.text,
                event.message.date,
                None
            )
            logger.info(f"Auto-indexed new message from {chat_id}")

# Add method to database if not exists
if not hasattr(Database, 'get_user_connections_by_channel'):
    def get_user_connections_by_channel(self, channel_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT user_id FROM user_connections WHERE channel_id = ?', (channel_id,))
        return cursor.fetchall()
    Database.get_user_connections_by_channel = get_user_connections_by_channel

# ============ FLASK FOR RENDER ============

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return jsonify({
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "bot": "Forwarding Bot v3.0"
    })

@app.route('/stats')
def bot_stats():
    return jsonify({
        "status": "running",
        "message": "Bot is active"
    })

# ============ MAIN ============

async def main():
    logger.info("🚀 Starting Forwarding Bot v3.0...")
    await bot.start(bot_token=BOT_TOKEN)
    logger.info("✅ Bot is running!")
    
    # Send startup message to admins
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "✅ Bot has been started successfully!")
        except:
            pass
    
    await bot.run_until_disconnected()

def run_bot():
    asyncio.run(main())

if __name__ == "__main__":
    import threading
    import os
    
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Start Flask server
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🔥 Starting web server on port {port}")
    app.run(host="0.0.0.0", port=port)
