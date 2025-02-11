from loguru import logger


# Configure logger
logger.add(
    "logs/audiokit_mcp.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

__all__ = ["logger"]
