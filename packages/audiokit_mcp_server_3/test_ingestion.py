import asyncio
import sys

from audiokit_mcp_server.config import settings
from audiokit_mcp_server.services.api_service import APIService
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

    # Initialize Redis cache with simpler config
    logger.debug("🔧 Initializing LOCAL Redis cache")
    setup_redis_cache(settings)

    # Initialize API service
    logger.debug("🚀 Initializing API service")
    api_service = APIService(settings)
    await api_service.startup()

    # Add artists to the queue
    artists = ["Rich Sibley", "Vozz Rich"]  # Example artists
    for artist in artists:
        await api_service.redis.sadd("pending:artists", artist)
        logger.debug(f"🎤 Added artist to queue: {artist}")

    input("Press Enter to continue...")
    # Process artists from the queue
    try:
        while True:
            # Get next artist from queue
            artist = await api_service.redis.spop("pending:artists")
            if not artist:
                logger.debug("🏁 Artist queue is empty")
                break

            logger.debug(f"🎶 Processing artist: {artist}")
            result = await api_service.ingest_soundcharts_api(artist)

            if result["status"] == "error":
                logger.error(f"❌ Failed to process artist {artist}: {result['error']}")
            elif result["status"] == "skipped":
                logger.warning(f"⚠️ Skipped artist {artist}: {result['reason']}")
            else:
                logger.debug(f"✅ Processed artist {artist}: {result}")

            # Optional: Add delay between processing if needed
            await asyncio.sleep(1)

        logger.success("🎉 All artists processed successfully")
    except asyncio.CancelledError:
        logger.info("Shutting down gracefully...")
    finally:
        # Ensure resources are closed
        logger.debug("🛑 Shutting down API service")
        await api_service.close()


if __name__ == "__main__":
    asyncio.run(main())
