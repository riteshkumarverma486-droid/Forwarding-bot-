import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS connections(
  user_id INTEGER,
  group_id INTEGER,
  channel_id INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS files(
  channel_id INTEGER,
  msg_id INTEGER,
  file_name TEXT
)
""")

def add_connection(u, g, c):
    cur.execute("INSERT INTO connections VALUES (?,?,?)", (u, g, c))
    conn.commit()

def get_connections(g):
    cur.execute("SELECT channel_id FROM connections WHERE group_id=?", (g,))
    return cur.fetchall()

def add_file(channel_id, msg_id, name):
    cur.execute("INSERT INTO files VALUES (?,?,?)", (channel_id, msg_id, name))
    conn.commit()

def search_files(q, limit=10):
    cur.execute(
        "SELECT channel_id, msg_id FROM files WHERE file_name LIKE ? LIMIT ?",
        (f"%{q}%", limit),
    )
    return cur.fetchall()
