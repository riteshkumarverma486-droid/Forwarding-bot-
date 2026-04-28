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

conn.commit()
