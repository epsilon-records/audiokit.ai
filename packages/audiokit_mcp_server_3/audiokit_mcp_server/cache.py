from functools import wraps
from typing import Any, Callable

import aioredis
from aiocache import cached
from aiocache.serializers import JsonSerializer
from structlog import get_logger


logger = get_logger()


def cache(ttl: int = 300) -> Callable:
    """Cache decorator with argument-aware keys."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Generate cache key with arguments
            key_parts = [
                func.__module__,
                func.__name__,
                *[str(arg) for arg in args[1:]],  # Skip self
                *[f"{k}={v}" for k, v in kwargs.items()],
            ]
            cache_key = ":".join(key_parts)

            logger.debug(
                "🔍 Cache lookup",
                function=func.__name__,
                key=cache_key,
            )

            # Use aiocache with the generated key
            return await cached(
                ttl=ttl,
                key=cache_key,
                serializer=JsonSerializer(),
            )(func)(*args, **kwargs)

        return wrapper

    return decorator


class Cache:
    def __init__(self, settings):
        self.settings = settings
        self.redis = None

    async def connect(self):
        """Connect to Redis."""
        self.redis = await aioredis.from_url(
            self.settings.redis_url,
            decode_responses=True,
            ssl=False,  # Explicitly disable SSL
        )
        logger.info("✅ Connected to Redis cache")
