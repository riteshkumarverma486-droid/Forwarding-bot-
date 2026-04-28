import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

# table
cur.execute("""
CREATE TABLE IF NOT EXISTS force_channels(
    channel_id TEXT
)
""")
conn.commit()

# ✅ ADD
def add_force_channel(channel):
    cur.execute("INSERT INTO force_channels VALUES (?)", (channel,))
    conn.commit()

# ✅ REMOVE
def remove_force_channel(channel):
    cur.execute("DELETE FROM force_channels WHERE channel_id = ?", (channel,))
    conn.commit()

# ✅ GET
def get_force_channels():
    cur.execute("SELECT channel_id FROM force_channels")
    return [i[0] for i in cur.fetchall()]
