from aiocache import RedisCache, caches
from structlog import get_logger


logger = get_logger()


def setup_redis_cache(settings):
    """
    Configure Redis cache with Upstash connection using all settings.

    Args:
        settings: Application settings object containing Redis configuration
    """
    try:
        logger.debug("🔧 Configuring LOCAL Redis cache")

        config = {
            "default": {
                "cache": "aiocache.RedisCache",
                "endpoint": settings.redis_host,
                "port": settings.redis_port,
                "timeout": settings.redis_timeout,
                "serializer": {
                    "class": "aiocache.serializers.JsonSerializer",
                },
            },
        }

        if settings.redis_password:
            config["default"]["password"] = settings.redis_password

        caches.set_config(config)
        logger.info("✅ Local Redis cache configured", config=config["default"])
    except Exception as e:
        logger.error("❌ Failed to configure Redis cache", error=str(e))
        raise


class LoggingRedisCache(RedisCache):
    async def _set(self, key, value, ttl=None, _conn=None):
        """Override set operation to add logging"""
        logger.debug(
            "📝 Writing to cache",
            key=key,
            ttl=ttl,
            value_type=type(value).__name__,
        )
        result = await super()._set(key, value, ttl, _conn)
        logger.debug(
            "✅ Cache write successful",
            key=key,
            ttl=ttl,
        )
        return result


class StrictRedisCache(RedisCache):
    async def _set(self, *args, **kwargs):
        """Override to disable silent failures"""
        try:
            return await super()._set(*args, **kwargs)
        except Exception as e:
            logger.error("🔥 Critical cache write failure", error=str(e))
            raise
