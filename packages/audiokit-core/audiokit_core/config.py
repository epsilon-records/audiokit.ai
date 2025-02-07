from pydantic import BaseSettings, Field
from pathlib import Path

class AudioKitConfig(BaseSettings):
    host: str = Field("127.0.0.1", env="AUDIOKIT_HOST")
    port: int = Field(8000, env="AUDIOKIT_PORT")
    log_level: str = Field("info", env="AUDIOKIT_LOG_LEVEL")
    audio_storage_path: Path = Field(Path("./audio_storage"), env="AUDIOKIT_STORAGE_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def load_config(config_path: Path = Path("config.yml")) -> AudioKitConfig:
    """Load configuration from YAML file with environment overrides"""
    # Implementation would parse YAML and merge with environment variables
    return AudioKitConfig()  # Simplified for example 