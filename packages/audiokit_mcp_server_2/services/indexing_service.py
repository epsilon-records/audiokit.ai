def index_content(item_id: str, content: str) -> bool:
    """
    Generate an embedding for the content and index it in the vector store.

    Args:
        item_id (str): Unique identifier for the content.
        content (str): Content to index.

    Returns:
        bool: True if indexing is successful, otherwise False.
    """
    from .embedding_service import get_embedding

    # Generate embedding from the content.
    embedding = get_embedding(content)

    # Use the vector store indexing function.
    from ..handlers.storage.vector_store import index_vector

    return index_vector(item_id, embedding)
