import asyncio
from telethon import TelegramClient
from telethon.errors import FloodWaitError
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MessageIndexer:
    def __init__(self, client: TelegramClient, database):
        self.client = client
        self.db = database
        self.is_indexing = False
    
    async def index_channel(self, channel_id, limit=1000):
        """Index messages from a channel"""
        if self.is_indexing:
            return {"status": "busy", "message": "Already indexing another channel"}
        
        self.is_indexing = True
        try:
            entity = await self.client.get_entity(channel_id)
            count = 0
            
            # Get recent messages
            async for message in self.client.iter_messages(entity, limit=limit):
                if message.text:
                    media_type = None
                    if message.photo:
                        media_type = 'photo'
                    elif message.video:
                        media_type = 'video'
                    elif message.document:
                        media_type = 'document'
                    
                    self.db.cache_message(
                        channel_id,
                        message.id,
                        message.text,
                        message.date,
                        media_type
                    )
                    count += 1
                    
                    # Rate limit protection
                    if count % 100 == 0:
                        await asyncio.sleep(1)
            
            return {"status": "success", "indexed": count}
            
        except FloodWaitError as e:
            logger.warning(f"Rate limited. Waiting {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            return await self.index_channel(channel_id, limit)
        except Exception as e:
            logger.error(f"Indexing error: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            self.is_indexing = False
    
    async def index_new_messages(self, channel_id, since_hours=24):
        """Index only new messages"""
        try:
            entity = await self.client.get_entity(channel_id)
            since_date = datetime.now() - timedelta(hours=since_hours)
            count = 0
            
            async for message in self.client.iter_messages(entity, offset_date=since_date):
                if message.text:
                    self.db.cache_message(
                        channel_id,
                        message.id,
                        message.text,
                        message.date
                    )
                    count += 1
            
            return count
        except Exception as e:
            logger.error(f"New message indexing error: {e}")
            return 0
