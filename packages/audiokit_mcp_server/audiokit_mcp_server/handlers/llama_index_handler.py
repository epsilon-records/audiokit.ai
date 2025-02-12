from typing import Dict, List

import pinecone
from fastapi import HTTPException
from llama_index import ServiceContext, StorageContext, VectorStoreIndex
from llama_index.vector_stores import PineconeVectorStore

from audiokit_mcp_server.core.config import settings
from audiokit_mcp_server.core.logger import logger


class LlamaIndexHandler:
    """Handler for LlamaIndex integration with Pinecone"""

    def __init__(self):
        # Initialize Pinecone
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT,
        )

        # Create Pinecone vector store
        self.vector_store = PineconeVectorStore(
            pinecone_index=pinecone.Index("audiokit-brain"),
        )

        # Create storage context
        storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store,
        )

        # Create service context
        self.service_context = ServiceContext.from_defaults()

        # Initialize index
        self.index = VectorStoreIndex(
            [],
            storage_context=storage_context,
            service_context=self.service_context,
        )

        logger.info("LlamaIndex handler initialized")

    async def query(self, query: str, top_k: int = 5) -> List[Dict]:
        """Query the index with natural language"""
        try:
            query_engine = self.index.as_query_engine(
                similarity_top_k=top_k,
            )
            response = query_engine.query(query)

            return [
                {
                    "text": node.text,
                    "metadata": node.metadata,
                    "score": node.score,
                }
                for node in response.source_nodes
            ]
        except Exception as e:
            logger.error(f"Query failed: {e!s}")
            raise HTTPException(status_code=500, detail=str(e))


# Create singleton instance
llama_index_handler = LlamaIndexHandler()
