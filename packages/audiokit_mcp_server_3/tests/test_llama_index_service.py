from audiokit_mcp_server.config import Settings
from audiokit_mcp_server.services.llama_index_service import LlamaIndexService


def test_llama_index_service_initialization():
    settings = Settings()
    service = LlamaIndexService(settings)
    assert service is not None
