from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field
from audiokit_core.config import BaseConfig, RateLimitConfig

class LoggingConfig(BaseModel):
    level: str = "INFO"
    directory: str = "logs"
    max_size: int = 10_000_000  # 10MB
    backup_count: int = 5
    console_output: bool = True

def load_config(config_path: Path = Path("config.yml")) -> ServerConfig:
    """Load configuration from YAML file."""
    if not config_path.exists():
        return ServerConfig()
    
    with open(config_path) as f:
        config_data = yaml.safe_load(f) or {}
        return ServerConfig(**config_data) 