from aiocache import caches
from structlog import get_logger


logger = get_logger()


def setup_redis_cache(redis_url: str, timeout: int = 5) -> None:
    """Configure Redis cache with proper URL parsing."""
    try:
        if "://" in redis_url:
            # Remove the redis:// or rediss:// prefix
            redis_url = redis_url.split("://")[1]

        # Handle Upstash-style URLs (user:password@host:port)
        if "@" in redis_url:
            credentials, host_port = redis_url.split("@")
            host, port = host_port.split(":")
        else:
            host, port = redis_url.split(":")

        # Extract database number if specified
        if "/" in port:
            port, db = port.split("/")
            db = int(db)
        else:
            db = 0  # Default to database 0 if not specified

        caches.set_config(
            {
                "default": {
                    "cache": "aiocache.RedisCache",
                    "endpoint": host,
                    "port": int(port),
                    "db": db,
                    "timeout": timeout,
                    "serializer": {
                        "class": "aiocache.serializers.JsonSerializer",
                    },
                },
            },
        )
        logger.info(
            "✅ Redis cache configured",
            host=host,
            port=port,
            db=db,
            timeout=timeout,
        )
    except Exception as e:
        logger.error(
            "❌ Failed to configure Redis cache",
            error=str(e),
        )
        raise
