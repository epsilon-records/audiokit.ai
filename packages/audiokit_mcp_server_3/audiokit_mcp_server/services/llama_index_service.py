from llama_index import ServiceContext, StorageContext, VectorStoreIndex
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.llms import OpenRouter
from structlog import get_logger


logger = get_logger()


class LlamaIndexService:
    def __init__(self, settings):
        """Initialize LlamaIndex service."""
        self.settings = settings
        self.service_context = self._create_service_context()
        self.storage_context = StorageContext.from_defaults()
        self.index = None
        logger.info("LlamaIndex service initialized")

    def _create_service_context(self) -> ServiceContext:
        """Create the service context with configured models."""
        llm = OpenRouter(
            api_key=self.settings.openrouter_api_key,
            api_base=self.settings.openrouter_base_url,
            model=self.settings.openrouter_model,
        )
        embed_model = HuggingFaceEmbedding(model_name=self.settings.embedding_model)
        return ServiceContext.from_defaults(
            llm=llm,
            embed_model=embed_model,
        )

    def get_index(self) -> VectorStoreIndex:
        """Get the existing vector store index."""
        if self.index is None:
            self.index = VectorStoreIndex(
                [],
                storage_context=self.storage_context,
                service_context=self.service_context,
            )
        return self.index

    async def query(self, query: str, top_k: int = 5) -> dict:
        """Query the index with natural language."""
        try:
            index = self.get_index()
            query_engine = index.as_query_engine(similarity_top_k=top_k)
            response = query_engine.query(query)

            return {
                "response": str(response),
                "sources": [
                    {
                        "text": node.text,
                        "metadata": node.metadata,
                        "score": node.score,
                    }
                    for node in response.source_nodes
                ],
            }
        except Exception as e:
            logger.error("Query failed", error=str(e))
            raise
