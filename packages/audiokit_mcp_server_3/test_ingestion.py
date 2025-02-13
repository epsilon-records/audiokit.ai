import asyncio
import sys
import traceback

from aiocache import caches
from audiokit_mcp_server.config import settings
from audiokit_mcp_server.services.api_service import APIService
from audiokit_mcp_server.services.deduplication_queue import DeduplicationQueue
from audiokit_mcp_server.utils.redis import setup_redis_cache
from loguru import logger


# Configure loguru with the correct log level
logger.remove()  # Remove default logger
logger.add(
    sys.stdout,
    level=settings.log_level.upper(),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level.icon} {level}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# Add emojis to log levels
logger.level("INFO", icon="ℹ️")
logger.level("DEBUG", icon="🐛")
logger.level("WARNING", icon="⚠️")
logger.level("ERROR", icon="❌")
logger.level("CRITICAL", icon="💥")
logger.level("SUCCESS", icon="✅")
logger.level("TRACE", icon="🔍")


async def main():
    # Initialize Redis
    setup_redis_cache(settings)

    # Create temp queue instance for cleanup
    dq = DeduplicationQueue(settings.redis_url)
    await dq.connect()
    await dq.clear()  # Use queue's clear method
    await dq.close()

    # Initialize Redis cache with simpler config
    logger.debug("🔧 Initializing LOCAL Redis cache")
    setup_redis_cache(settings)

    # Clear queue before starting
    cache = caches.get("default")
    await cache.raw("flushdb")
    logger.debug("🧪 Cleared Redis cache for test ingestion")

    # Verify cache backend
    cache = caches.get("default")
    logger.debug(
        "🔍 Cache backend verification - type: {}, redis_connected: {}",
        type(cache).__name__,
        cache.endpoint == settings.redis_host,
    )

    # Test direct write/read
    test_key = "validation_key"
    await cache.set(test_key, "test_value", ttl=10)  # Explicit 10s TTL
    value = await cache.get(test_key)
    logger.debug(
        "🧪 Direct cache test - key: {}, stored_value: {}, redis_exists: {}",
        test_key,
        value,
        await cache.exists(test_key),
    )

    # After cache setup
    info = await cache.raw("info", "memory")
    logger.debug("🧠 Redis Memory Info: {}", info)

    # Initialize API service
    logger.debug("🚀 Initializing API service")
    api_service = APIService(settings)
    await api_service.startup()  # Explicitly call startup

    # Test artist ingestion
    artist_name = "Kanye West"
    try:
        logger.info("🎤 Starting artist ingestion - artist: {}", artist_name)
        result = await api_service.ingest_soundcharts_api(artist_name)
        logger.info("🎉 Ingestion completed successfully - result: {}", result)
    except Exception as e:
        # Extract more detailed error information
        error_details = str(e)
        if hasattr(e, "errors"):
            error_details = "\n".join(
                f"Field: {'.'.join(map(str, err['loc']))} - {err['msg']}"
                for err in getattr(e, "errors", list)()
            )

        logger.error(
            "🚨 Ingestion failed - artist: {}\nValidation Errors:\n{}\nStack Trace:\n{}",
            artist_name,
            error_details,
            traceback.format_exc(),
        )
        # Add additional debug information
        logger.debug(
            "Failed artist data structure: {}",
            {
                "artist_name": artist_name,
                "error_type": type(e).__name__,
                "error_fields": getattr(e, "fields", None),
                "input_data": getattr(
                    e,
                    "input_data",
                    None,
                ),  # Add input data if available
            },
        )
    finally:
        # Ensure resources are closed
        logger.debug("🛑 Shutting down API service")
        await api_service.close()


if __name__ == "__main__":
    asyncio.run(main())
