from typing import List

from llama_index.core import VectorStoreIndex
from llama_index.core.settings import Settings as LlamaSettings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter
from structlog import get_logger

from ..utils.embedding_utils import pad_embedding


logger = get_logger()


class LlamaIndexService:
    def __init__(self, settings):
        """Initialize LlamaIndex Service."""
        self.settings = settings
        self._initialize_pinecone()
        self._setup_llama_settings()
        # For simplicity, we create a dummy index.
        self.index = None
        logger.info("LlamaIndexService initialized")

    def _initialize_pinecone(self):
        """Initialize Pinecone connection."""
        try:
            from pinecone import Pinecone  # Use the new API

            self.pc = Pinecone(api_key=self.settings.pinecone_api_key)
            logger.info("Pinecone initialized")
        except Exception as e:
            logger.error("Failed to initialize Pinecone", error=str(e))
            raise

    def _setup_llama_settings(self):
        """Setup LlamaIndex settings with configured models."""

        # Create custom embedding model that pads the output
        class PaddedHuggingFaceEmbedding(HuggingFaceEmbedding):
            def get_text_embedding(self, text: str) -> List[float]:
                embedding = super().get_text_embedding(text)
                # Ensure the embedding is a list (in case it is a numpy array)
                if not isinstance(embedding, list):
                    embedding = (
                        embedding.tolist()
                        if hasattr(embedding, "tolist")
                        else list(embedding)
                    )
                return pad_embedding(embedding, target_dim=1024)

            def get_query_embedding(self, query_text: str) -> List[float]:
                # Ensure query embeddings are also padded
                return self.get_text_embedding(query_text)

        # Initialize embedding model
        embed_model = PaddedHuggingFaceEmbedding(
            model_name=self.settings.embedding_model,
        )

        # Initialize LLM
        llm = OpenRouter(
            api_key=self.settings.openrouter_api_key,
            model=self.settings.openrouter_model,
        )

        # Update LlamaIndex settings
        LlamaSettings.embed_model = embed_model
        LlamaSettings.llm = llm
        logger.info("LlamaIndex settings configured")

    def get_index(self) -> VectorStoreIndex:
        """Get the existing vector store index."""
        if self.index is None:
            # For demonstration, simply return an empty index.
            self.index = VectorStoreIndex([])
        return self.index

    async def query(self, query: str, top_k: int = 5) -> dict:
        """Query the index with natural language."""
        logger.info("Executing query", query=query, top_k=top_k)
        try:
            index = self.get_index()
            query_engine = index.as_query_engine(similarity_top_k=top_k)
            response = query_engine.query(query)
        except Exception:
            logger.exception("Query execution failed")
            raise

        sources = []
        if hasattr(response, "source_nodes") and response.source_nodes:
            for node in response.source_nodes:
                try:
                    if isinstance(node, dict):
                        text = node.get("text", "")
                        metadata = node.get("metadata", {})
                        score = float(node.get("score", 0))
                    else:
                        text = getattr(node, "text", "")
                        metadata = getattr(node, "metadata", {})
                        score = float(getattr(node, "score", 0))
                    sources.append(
                        {
                            "text": text,
                            "metadata": metadata,
                            "score": score,
                        }
                    )
                except Exception as e:
                    logger.warning(
                        "Node processing failed, skipping node", error=str(e)
                    )
        answer = str(response)
        return {"answer": answer, "sources": sources}

    async def hybrid_search(self, query: str, top_k: int = 5) -> dict:
        """Perform hybrid search combining vector and keyword search."""
        try:
            index = self.get_index()
            retriever = index.as_retriever(
                similarity_top_k=top_k,
                vector_store_query_mode="hybrid",
            )
            nodes = retriever.retrieve(query)

            return {
                "results": [
                    {
                        "text": node.text,
                        "metadata": node.metadata,
                        "score": node.score,
                    }
                    for node in nodes
                ],
            }
        except Exception as e:
            logger.error("Hybrid search failed", error=str(e))
            raise

    async def query_with_filters(
        self,
        query: str,
        filters: dict,
        top_k: int = 5,
    ) -> dict:
        """Query with metadata filters."""
        try:
            index = self.get_index()
            query_engine = index.as_query_engine(
                similarity_top_k=top_k,
                filters=filters,
            )
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
            logger.error("Filtered query failed", error=str(e))
            raise

    def get_index_stats(self) -> dict:
        """Get statistics about the index."""
        try:
            index = self.get_index()
            return {
                "document_count": len(index.docstore.docs),
                "node_count": len(index.docstore.nodes),
                "vector_count": index.vector_store.client.describe_index_stats(),
            }
        except Exception as e:
            logger.error("Failed to get index stats", error=str(e))
            raise
