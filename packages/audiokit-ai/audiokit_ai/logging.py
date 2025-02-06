import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_dir: Path = Path("logs")):
    log_dir.mkdir(exist_ok=True)
    
    # Main application logger
    logger = logging.getLogger("audiokit")
    logger.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_dir / "audiokit.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        "%(levelname)s: %(message)s"
    ))
    logger.addHandler(console_handler)

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