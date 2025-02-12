from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "AudioKit MCP Server"
    debug: bool = False
    mcp_version: str = "2.0"

    class Config:
        env_file = ".env"
