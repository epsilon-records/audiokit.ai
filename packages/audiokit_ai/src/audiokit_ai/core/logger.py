from loguru import logger
import sys

# Custom log format with emojis
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level.icon} {level}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Configure logger
logger.remove()  # Remove default logger
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level="INFO",
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

# Export logger for use in other modules
__all__ = ["logger"] 