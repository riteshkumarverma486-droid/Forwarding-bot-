import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# comma separated usernames without @
FORCE_JOIN = os.getenv("FORCE_JOIN", "")  # e.g. Backup_Channel42,Channel2

ADMINS = [int(x) for x in os.getenv("ADMINS", "").split(",") if x]
