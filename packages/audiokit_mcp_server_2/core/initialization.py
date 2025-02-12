from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore

from ..core.config import settings


def initialize_pinecone_index():
    """
    Initialize the Pinecone index at application startup.
    """
    try:
        vector_store = PineconeVectorStore(
            index_name="audiokit-brain",
            environment=settings.pinecone_env,
            api_key=settings.pinecone_api_key,
        )

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        return VectorStoreIndex([], storage_context=storage_context)

    except Exception as e:
        raise Exception(f"Failed to initialize Pinecone index: {e!s}")
