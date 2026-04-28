cursor.execute("""
CREATE TABLE IF NOT EXISTS force_channels (
    channel TEXT
)
""")

def add_force_channel(channel):
    cursor.execute("INSERT INTO force_channels VALUES (?)", (channel,))
    conn.commit()

def remove_force_channel(channel):
    cursor.execute("DELETE FROM force_channels WHERE channel=?", (channel,))
    conn.commit()

def get_force_channels():
    cursor.execute("SELECT channel FROM force_channels")
    return [x[0] for x in cursor.fetchall()]
