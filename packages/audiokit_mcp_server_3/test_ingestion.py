import asyncio

from aiocache import caches
from audiokit_mcp_server.config import settings
from audiokit_mcp_server.services.api_service import APIService
from audiokit_mcp_server.utils.redis import setup_redis_cache
from structlog import get_logger


logger = get_logger()


async def main():
    # Initialize Redis cache with simpler config
    logger.debug("🔧 Initializing LOCAL Redis cache")
    setup_redis_cache(settings)

    # Verify cache backend
    cache = caches.get("default")
    logger.debug(
        "🔍 Cache backend verification",
        type=type(cache).__name__,
        redis_connected=cache.endpoint == settings.redis_host,
    )

    # Test direct write/read
    test_key = "validation_key"
    await cache.set(test_key, "test_value", ttl=10)  # Explicit 10s TTL
    value = await cache.get(test_key)
    logger.debug(
        "🧪 Direct cache test",
        key=test_key,
        stored_value=value,
        redis_exists=await cache.exists(test_key),
    )

    # After cache setup
    info = await cache.raw("info", "memory")
    logger.debug("🧠 Redis Memory Info", memory_info=info)

    # Initialize API service
    logger.debug("🚀 Initializing API service")
    api_service = APIService(settings)
    await api_service.startup()  # Explicitly call startup

    # Test artist ingestion
    artist_name = "Kanye West"
    try:
        logger.info("🎤 Starting artist ingestion", artist=artist_name)
        result = await api_service.ingest_soundcharts_api(artist_name)
        logger.info("🎉 Ingestion completed successfully", result=result)
    except Exception as e:
        logger.error("🚨 Ingestion failed", artist=artist_name, error=str(e))
    finally:
        # Ensure resources are closed
        logger.debug("🛑 Shutting down API service")
        await api_service.close()


if __name__ == "__main__":
    asyncio.run(main())
