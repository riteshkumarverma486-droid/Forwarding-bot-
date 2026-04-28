import sqlite3

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    link TEXT
)
""")
conn.commit()


def save_movie(text, link):
    cursor.execute("INSERT INTO movies (text, link) VALUES (?, ?)", (text, link))
    conn.commit()


def search_movie(query):
    cursor.execute("SELECT text, link FROM movies WHERE text LIKE ?", ('%' + query + '%',))
    return cursor.fetchall()
