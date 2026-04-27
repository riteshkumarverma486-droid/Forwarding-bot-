import sqlite3
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path='forwarding_bot.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.setup_tables()
    
    def setup_tables(self):
        cursor = self.conn.cursor()
        
        # User connections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_connections (
                user_id INTEGER,
                channel_id INTEGER,
                channel_title TEXT,
                group_id INTEGER,
                group_title TEXT,
                connected_at TIMESTAMP,
                PRIMARY KEY (user_id, channel_id)
            )
        ''')
        
        # Message cache table (fast search ke liye)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_cache (
                channel_id INTEGER,
                message_id INTEGER,
                message_text TEXT,
                message_date TIMESTAMP,
                media_type TEXT,
                PRIMARY KEY (channel_id, message_id)
            )
        ''')
        
        # Search history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                user_id INTEGER,
                search_query TEXT,
                results_count INTEGER,
                search_time TIMESTAMP
            )
        ''')
        
        # Rate limiting table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limits (
                user_id INTEGER,
                search_count INTEGER,
                last_reset TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        logger.info("Database setup complete")
    
    # ========== CONNECTION METHODS ==========
    def add_connection(self, user_id, channel_id, channel_title, group_id, group_title):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_connections 
            (user_id, channel_id, channel_title, group_id, group_title, connected_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, channel_id, channel_title, group_id, group_title, datetime.now()))
        self.conn.commit()
    
    def get_user_connections(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT channel_id, channel_title, group_id, group_title 
            FROM user_connections WHERE user_id = ?
        ''', (user_id,))
        return cursor.fetchall()
    
    def remove_connection(self, user_id, channel_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM user_connections WHERE user_id = ? AND channel_id = ?', 
                      (user_id, channel_id))
        self.conn.commit()
    
    def get_group_for_channel(self, user_id, channel_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT group_id FROM user_connections 
            WHERE user_id = ? AND channel_id = ?
        ''', (user_id, channel_id))
        result = cursor.fetchone()
        return result[0] if result else None
    
    # ========== MESSAGE CACHE METHODS ==========
    def cache_message(self, channel_id, message_id, message_text, message_date, media_type=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO message_cache 
            (channel_id, message_id, message_text, message_date, media_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (channel_id, message_id, message_text[:2000], message_date, media_type))
        self.conn.commit()
    
    def search_messages(self, channel_ids, query, limit=10):
        cursor = self.conn.cursor()
        placeholders = ','.join('?' * len(channel_ids))
        results = []
        
        for channel_id in channel_ids:
            cursor.execute('''
                SELECT channel_id, message_id, message_text, message_date, media_type
                FROM message_cache 
                WHERE channel_id = ? AND message_text LIKE ? 
                ORDER BY message_date DESC LIMIT ?
            ''', (channel_id, f'%{query}%', limit))
            results.extend(cursor.fetchall())
        
        # Sort by date and limit
        results.sort(key=lambda x: x[3], reverse=True)
        return results[:limit]
    
    # ========== SEARCH HISTORY ==========
    def log_search(self, user_id, query, results_count):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO search_history (user_id, search_query, results_count, search_time)
            VALUES (?, ?, ?, ?)
        ''', (user_id, query, results_count, datetime.now()))
        self.conn.commit()
    
    def get_recent_searches(self, user_id, limit=10):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT search_query, results_count, search_time 
            FROM search_history 
            WHERE user_id = ? 
            ORDER BY search_time DESC LIMIT ?
        ''', (user_id, limit))
        return cursor.fetchall()
    
    # ========== RATE LIMITING ==========
    def check_rate_limit(self, user_id, max_searches=10):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT search_count, last_reset FROM rate_limits WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        
        now = datetime.now()
        
        if not result:
            cursor.execute('''
                INSERT INTO rate_limits (user_id, search_count, last_reset)
                VALUES (?, 1, ?)
            ''', (user_id, now))
            self.conn.commit()
            return True
        
        count, last_reset = result
        last_reset = datetime.fromisoformat(last_reset)
        
        # Reset counter if more than 1 minute has passed
        if (now - last_reset).total_seconds() > 60:
            cursor.execute('''
                UPDATE rate_limits SET search_count = 1, last_reset = ? 
                WHERE user_id = ?
            ''', (now, user_id))
            self.conn.commit()
            return True
        
        if count >= max_searches:
            return False
        
        cursor.execute('''
            UPDATE rate_limits SET search_count = search_count + 1 
            WHERE user_id = ?
        ''', (user_id,))
        self.conn.commit()
        return True
    
    def close(self):
        self.conn.close()
