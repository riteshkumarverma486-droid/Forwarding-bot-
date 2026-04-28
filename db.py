import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

# ✅ Force Channels Table
cur.execute("""
CREATE TABLE IF NOT EXISTS force_channels(
    channel_id TEXT
)
""")

# ✅ Connections Table (PEHLE CREATE KARO)
cur.execute("""
CREATE TABLE IF NOT EXISTS connections(
    user_id INTEGER,
    group_id INTEGER,
    channel_id TEXT
)
""")

conn.commit()

# ✅ ADD FORCE CHANNEL
def add_force_channel(channel):
    cur.execute("INSERT INTO force_channels VALUES (?)", (channel,))
    conn.commit()

# ✅ REMOVE FORCE CHANNEL
def remove_force_channel(channel):
    cur.execute("DELETE FROM force_channels WHERE channel_id = ?", (channel,))
    conn.commit()

# ✅ GET FORCE CHANNELS
def get_force_channels():
    cur.execute("SELECT channel_id FROM force_channels")
    return [i[0] for i in cur.fetchall()]

# ✅ ADD CONNECTION
def add_connection(user_id, group_id, channel_id):
    cur.execute(
        "INSERT INTO connections (user_id, group_id, channel_id) VALUES (?, ?, ?)",
        (user_id, group_id, channel_id)
    )
    conn.commit()
