"""Configuration management."""

from dataclasses import dataclass
import os


@dataclass
class Settings:
    """Application settings."""

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
