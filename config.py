import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API (my.telegram.org se)
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# Bot Settings
SEARCH_LIMIT = 50          # Maximum search results
MESSAGE_CACHE_DAYS = 30    # Kitne din purani messages cache mein rakhein
MAX_SEARCH_PER_MINUTE = 10 # Rate limiting

# Admin IDs (Optional)
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]
