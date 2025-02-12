from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore

from ..core.config import settings


def perform_search(query_embedding: list) -> dict:
    """
    Perform a vector similarity search using Pinecone via LlamaIndex.
    """
    try:
        # Initialize Pinecone vector store
        vector_store = PineconeVectorStore(
            index_name="audiokit-brain",
            environment=settings.pinecone_env,
            api_key=settings.pinecone_api_key,
        )

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex([], storage_context=storage_context)

        # Perform similarity search
        query_engine = index.as_query_engine(similarity_top_k=5)
        response = query_engine.query(query_embedding)

        return {
            "results": [
                {
                    "text": node.text,
                    "metadata": node.metadata,
                    "score": node.score,
                }
                for node in response.source_nodes
            ],
        }

    except Exception as e:
        return {"error": str(e)}
