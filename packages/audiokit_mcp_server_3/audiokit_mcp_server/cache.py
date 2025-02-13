import functools
import json

from aiocache import cached, caches
from aiocache.serializers import JsonSerializer
from structlog import get_logger


logger = get_logger()


def cache(key_arg_index: int = 1):
    """
    Decorator factory for caching with aiocache.

    Args:
        key_arg_index: Index of the argument to use as cache key (default: 1)
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            ttl = getattr(self, "cache_ttl", 86400)  # Uses settings.redis_cache_ttl
            cache_key = f"{func.__module__}:{func.__name__}:{args[key_arg_index] if len(args) > key_arg_index else 'default'}"

            # Try to get from cache first
            try:
                cached_value = await cached(
                    ttl=ttl,
                    serializer=JsonSerializer(),
                    key_builder=lambda f, *args, **kwargs: cache_key,
                )(func)(self, *args, **kwargs)
                logger.debug(
                    "🔍 Cache hit",
                    key=cache_key,
                    function=func.__name__,
                )
                return cached_value
            except Exception as e:
                logger.debug(
                    "❌ Cache miss",
                    key=cache_key,
                    function=func.__name__,
                    error=str(e),
                )
                # Execute the function and cache the result
                result = await func(self, *args, **kwargs)

                # Test serialization
                try:
                    json.dumps(result)
                except TypeError as e:
                    logger.error("❌ Failed to serialize result", error=str(e))
                    return result

                # Write to cache explicitly
                try:
                    cache = caches.get("default")
                    logger.debug(
                        "📝 Writing to cache",
                        key=cache_key,
                        ttl=ttl,
                        value_type=type(result).__name__,
                    )
                    await cache.set(cache_key, result, ttl=ttl)
                    # Verify write immediately
                    exists = await cache.exists(cache_key)
                    logger.debug(
                        "🔎 Immediate cache verification",
                        key=cache_key,
                        exists=exists,
                        ttl=await cache.ttl(cache_key),
                    )
                except Exception as e:
                    logger.error("Cache write failed", error=str(e))
                return result

        return wrapper

    return decorator
