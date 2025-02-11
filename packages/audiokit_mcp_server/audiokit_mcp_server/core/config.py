from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Server settings
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ENV: str = "development"

    # API configurations
    OPENROUTER_API_KEY: str
    OPENROUTER_API_BASE: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "anthropic/claude-3.5-sonnet"

    # Soundcharts API
    SOUNDCHARTS_APP_ID: str
    SOUNDCHARTS_API_KEY: str
    SOUNDCHARTS_API_BASE: str = "https://api.soundcharts.com/api/v2"

    # Weaviate settings
    WEAVIATE_URL: str  # This should be the full URL of your Weaviate instance (with protocol, e.g., "https://my-weaviate-instance.com")
    WEAVIATE_API_KEY: Optional[str] = None

    # RAG settings
    MIN_RELEVANCE_SCORE: float = 0.7
    MAX_INSIGHTS: int = 10
    TIME_WEIGHTS: dict = {
        "24h": 1.0,
        "7d": 0.9,
        "30d": 0.8,
        "90d": 0.7,
        "older": 0.6,
    }

    # Audio processing
    AUDIO_STORAGE_PATH: str = "/opt/tmp"
    MAX_FILE_SIZE: int = 100_000_000  # 100MB
    SUPPORTED_FORMATS: List[str] = ["wav", "mp3", "flac", "aac"]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding="utf-8",
    )


settings = Settings()
