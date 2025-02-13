from functools import wraps
from typing import Any, Callable

from aiocache import cached
from aiocache.serializers import JsonSerializer
from structlog import get_logger


logger = get_logger()


def redis_cache(ttl: int = 86400) -> Callable:
    """
    Decorator to cache async function results in Redis with a TTL.

    Args:
        ttl: Time-to-live in seconds (default: 1 day)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @cached(ttl=ttl, serializer=JsonSerializer(), namespace="soundcharts")
        async def wrapper(*args, **kwargs) -> Any:
            cache_key = f"{func.__module__}:{func.__name__}:{args}:{kwargs}"

            try:
                # Check cache
                logger.debug("🔍 Checking cache", cache_key=cache_key)
                result = await wrapper.cache.get(cache_key)

                if result is not None:
                    logger.debug("✅ Cache hit", cache_key=cache_key)
                    return result

                logger.debug("❌ Cache miss", cache_key=cache_key)

                # Execute function
                result = await func(*args, **kwargs)

                # Store result in cache
                try:
                    await wrapper.cache.set(cache_key, result, ttl=ttl)
                    logger.debug(
                        "💾 Cached result",
                        cache_key=cache_key,
                        ttl=ttl,
                    )
                except Exception as e:
                    logger.error(
                        "🚨 Failed to cache result",
                        cache_key=cache_key,
                        error=str(e),
                    )

                return result
            except Exception as e:
                logger.error(
                    "🚨 Cache operation failed",
                    cache_key=cache_key,
                    error=str(e),
                )
                return await func(*args, **kwargs)

        return wrapper

    return decorator
