import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS connections (
    user_id INTEGER,
    group_id INTEGER,
    channel_id INTEGER
)
""")

conn.commit()

def add_connection(user_id, group_id, channel_id):
    cursor.execute("INSERT INTO connections VALUES (?, ?, ?)", (user_id, group_id, channel_id))
    conn.commit()

def get_connections(group_id):
    cursor.execute("SELECT channel_id FROM connections WHERE group_id=?", (group_id,))
    return cursor.fetchall()
