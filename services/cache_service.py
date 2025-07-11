import asyncio
import json
from typing import Any, Optional, Dict
import aioredis
from datetime import datetime, timedelta
import logging

from config.settings import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis = None
        self.ttl = settings.CACHE_TTL
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            logger.info("Cache service initialized successfully")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory cache: {str(e)}")
            self.redis = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis:
                value = await self.redis.get(key)
                if value:
                    return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            if self.redis:
                ttl = ttl or self.ttl
                await self.redis.setex(key, ttl, json.dumps(value))
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.redis:
                await self.redis.delete(key)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            return False
    
    async def clear_cache(self) -> bool:
        """Clear all cache"""
        try:
            if self.redis:
                await self.redis.flushdb()
                return True
            return False
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if self.redis:
                info = await self.redis.info()
                return {
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory': info.get('used_memory_human', '0B'),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0)
                }
            return {'status': 'Redis not available'}
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {'error': str(e)}
