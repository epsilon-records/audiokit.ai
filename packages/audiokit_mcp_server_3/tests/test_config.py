from audiokit_mcp_server.config import Settings


def test_settings_loading():
    settings = Settings()
    assert settings.pinecone_api_key is not None
    assert settings.openrouter_api_key is not None
    assert settings.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    assert settings.index_name == "audiokit-brain"
