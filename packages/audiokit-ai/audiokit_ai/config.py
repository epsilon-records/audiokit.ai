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

class ServerConfig(BaseConfig):
    """Server configuration model."""
    host: str = Field("0.0.0.0", description="Server host address")
    port: int = Field(8000, description="Server port")
    log_level: str = Field("info", description="Logging level")
    api_key: str = Field("test-key", description="Default API key")
    max_file_size: int = Field(209_715_200, description="Max file size in bytes (200MB)")
    rate_limit: int = Field(60, description="Requests per minute per API key")
    redis_url: Optional[str] = Field(None, description="Redis connection URL")
    debug: bool = Field(False, description="Debug mode")
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    rate_limiting: RateLimitConfig = Field(default_factory=RateLimitConfig)
    enable_docs: bool = Field(False, description="Enable API documentation")

def load_config(config_path: Path = Path("config.yml")) -> ServerConfig:
    """Load configuration from YAML file."""
    if not config_path.exists():
        return ServerConfig()
    
    with open(config_path) as f:
        config_data = yaml.safe_load(f) or {}
        return ServerConfig(**config_data) 