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
        @cached(
            ttl=ttl,
            serializer=JsonSerializer(),
            namespace="soundcharts",
            key_builder=lambda f,
            *args,
            **kwargs: f"{f.__module__}:{f.__name__}:{args[1] if len(args) > 1 else 'default'}",
        )
        async def wrapper(*args, **kwargs) -> Any:
            cache_key = f"{func.__module__}:{func.__name__}:{args[1] if len(args) > 1 else 'default'}"
            try:
                logger.debug("🔍 Checking cache", cache_key=cache_key)
                result = await func(*args, **kwargs)
                logger.info(
                    "💾 Cached result",
                    cache_key=cache_key,
                    ttl=ttl,
                    function=func.__name__,
                )
                return result
            except Exception as e:
                logger.error(
                    "🚨 Cache operation failed",
                    cache_key=cache_key,
                    error=str(e),
                )
                raise

        return wrapper

    return decorator
