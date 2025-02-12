from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "AudioKit MCP Server"
    debug: bool = False
    mcp_version: str = "3.0"
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/chatgpt-4o-latest"  # Default OpenRouter model
    embedding_model: str = (
        "sentence-transformers/all-MiniLM-L6-v2"  # Open-source Hugging Face model
    )
    index_name: str = "audiokit-brain"  # Fixed index name

    class Config:
        env_file = ".env"
