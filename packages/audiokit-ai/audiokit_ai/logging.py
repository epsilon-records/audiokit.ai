import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Any
import json
from .config import ServerConfig

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        return json.dumps(log_data)

def setup_logging(config: ServerConfig) -> None:
    """Configure logging system"""
    log_dir = Path(config.logging.directory)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(config.logging.level.upper())

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        filename=log_dir / "audiokit.log",
        maxBytes=config.logging.max_size,
        backupCount=config.logging.backup_count
    )
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)

    # Console handler
    if config.logging.console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(console_handler)

    # Capture warnings
    logging.captureWarnings(True)

class StructuredLogger:
    """Enhanced structured logging for AudioKit."""
    
    def __init__(self, name: str, log_dir: Path):
        self.logger = logging.getLogger(name)
        self.log_dir = log_dir
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Configure logging handlers."""
        # Ensure log directory exists
        self.log_dir.mkdir(exist_ok=True)
        
        # Application log
        app_handler = RotatingFileHandler(
            self.log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        app_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # Error log
        error_handler = RotatingFileHandler(
            self.log_dir / "error.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
            'Exception: %(exc_info)s'
        ))
        
        # Add handlers
        self.logger.addHandler(app_handler)
        self.logger.addHandler(error_handler) 