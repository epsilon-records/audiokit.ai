import os

from pydantic_settings import BaseSettings


class Config:
    """
    Configuration class for AudioKit MCP Server.
    Loads configuration from environment variables.
    """

    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "your-api-key")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "your-pinecone-api-key")
    PINECONE_ENV: str = os.getenv("PINECONE_ENV", "us-west1-gcp")
    # Add more configuration items as needed


class Settings(BaseSettings):
    pinecone_api_key: str
    pinecone_env: str = "us-west1-gcp"
    openrouter_api_key: str
    audio_storage_path: str = "/var/audiokit/storage"

    class Config:
        env_file = ".env"


class MCPConfig:
    MCP_ENABLED: bool = True
    MCP_VERSION: str = "1.0.0"
    MCP_RESOURCES: list = ["audio-ingestion", "text-ingestion"]


config = Config()
settings = Settings()
