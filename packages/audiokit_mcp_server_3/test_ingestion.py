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
    api_service = None
    try:
        # Initialize Redis
        setup_redis_cache(settings)

        # Initialize API service
        logger.debug("🚀 Initializing API service")
        api_service = APIService(settings)
        await api_service.startup()

        # Create test artist data
        test_artist = {
            "name": "Rich Sibley",
            "uuid": "63788d70-924b-4f6a-9329-bbb34b8e771e",
        }

        # Add artist to queue
        await api_service._add_to_pending_list(test_artist["name"], test_artist["uuid"])

        input("Press Enter to continue...")

        # Process artists from the queue
        await api_service.process_pending_artists()

    except Exception as e:
        logger.error("Error during main execution", error=str(e))
    finally:
        if api_service:
            await api_service.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "Event loop is closed" not in str(e):
            raise
