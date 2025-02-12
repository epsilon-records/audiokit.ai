from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "AudioKit MCP Server"
    debug: bool = False
    mcp_version: str = "3.0"
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/chatgpt-4o-latest"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    index_name: str = "audiokit-brain"
    pinecone_api_key: str
    pinecone_environment: str = "us-west1-gcp"
    acoustid_api_key: str

    model_config = SettingsConfigDict(env_file=".env")
