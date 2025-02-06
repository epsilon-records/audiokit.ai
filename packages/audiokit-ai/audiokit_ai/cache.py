"""Caching system for AudioKit AI server."""
from typing import Optional, Any, Union
import hashlib
import json
from datetime import datetime, timedelta
import asyncio
from functools import wraps
import redis.asyncio as redis
from pydantic import BaseModel

class CacheConfig(BaseModel):
    """Cache configuration."""
    url: str = "redis://localhost:6379/0"
    default_ttl: int = 3600  # 1 hour
    enabled: bool = True

class CacheKey(BaseModel):
    """Cache key with metadata."""
    key: str
    expires_at: Optional[datetime] = None
    tags: list[str] = []

class Cache:
    """Redis-based caching implementation."""
    
    def __init__(self, config: CacheConfig):
        """Initialize cache.
        
        Args:
            config: Cache configuration
        """
        self.config = config
        self.redis = redis.from_url(config.url) if config.enabled else None
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found, else None
        """
        if not self.redis:
            return None
            
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
        
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[list[str]] = None
    ) -> None:
        """Set cache value.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            tags: Optional tags for grouping
        """
        if not self.redis:
            return
            
        # Store value
        ttl = ttl or self.config.default_ttl
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )
        
        # Store metadata
        meta = CacheKey(
            key=key,
            expires_at=datetime.utcnow() + timedelta(seconds=ttl),
            tags=tags or []
        )
        await self.redis.hset(
            "cache_meta",
            key,
            meta.json()
        )
        
        # Update tag indices
        if tags:
            for tag in tags:
                await self.redis.sadd(f"tag:{tag}", key)
                
    async def invalidate(self, key: str) -> None:
        """Invalidate cached value.
        
        Args:
            key: Cache key
        """
        if not self.redis:
            return
            
        # Remove value and metadata
        await asyncio.gather(
            self.redis.delete(key),
            self.redis.hdel("cache_meta", key)
        )
        
    async def invalidate_by_tag(self, tag: str) -> None:
        """Invalidate all values with tag.
        
        Args:
            tag: Cache tag
        """
        if not self.redis:
            return
            
        # Get keys for tag
        keys = await self.redis.smembers(f"tag:{tag}")
        if not keys:
            return
            
        # Remove values, metadata and tag
        await asyncio.gather(
            self.redis.delete(*keys),
            self.redis.hdel("cache_meta", *keys),
            self.redis.delete(f"tag:{tag}")
        )

def cached(
    ttl: Optional[int] = None,
    tags: Optional[list[str]] = None,
    key_prefix: str = ""
):
    """Cache decorator for API endpoints.
    
    Args:
        ttl: Optional TTL override
        tags: Optional cache tags
        key_prefix: Optional key prefix
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not self.cache or not self.cache.redis:
                return await func(self, *args, **kwargs)
                
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            key = hashlib.sha256(
                ":".join(key_parts).encode()
            ).hexdigest()
            
            # Check cache
            cached_value = await self.cache.get(key)
            if cached_value is not None:
                return cached_value
                
            # Get fresh value
            value = await func(self, *args, **kwargs)
            
            # Cache result
            await self.cache.set(key, value, ttl, tags)
            return value
            
        return wrapper
    return decorator 