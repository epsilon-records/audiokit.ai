from pathlib import Path
from loguru import logger
import sys
from typing import Dict, Any
from .config import ServerConfig

# Custom log levels and emojis
LOG_LEVEL_EMOJIS = {
    "TRACE": "🔍",
    "DEBUG": "🐛",
    "INFO": "ℹ️",
    "SUCCESS": "✅",
    "WARNING": "⚠️",
    "ERROR": "🚨",
    "CRITICAL": "💥"
}

def setup_logging(config: ServerConfig) -> None:
    """Configure Loguru logging with emojis and pretty formatting"""
    log_dir = Path(config.logging.directory)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Remove default handler
    logger.remove()

    # Console formatting
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level.icon}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=config.logging.level.upper(),
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    # File logging (structured JSON)
    logger.add(
        log_dir / "audiokit.log",
        rotation=f"{config.logging.max_size} MB",
        retention=f"{config.logging.backup_count} days",
        format="{message}",
        serialize=True,
        level="DEBUG",
        enqueue=True,
        compression="zip"
    )

    # Add custom level icons
    for level, emoji in LOG_LEVEL_EMOJIS.items():
        logger.level(level, icon=emoji)

    # Add processor for request context
    logger.configure(extra={"user": None, "job_id": None})

class StructuredLogger:
    """Enhanced structured logging with Loguru"""
    
    def __init__(self, name: str = "audiokit"):
        self.logger = logger.bind(module=name)
        
    def __getattr__(self, name: str):
        return getattr(self.logger, name)

# Example usage:
# logger.success("Service started successfully!")
# logger.error("Something went wrong!", user="admin", job_id="123") 