from typing import List

from llama_index.embeddings.openai import OpenAIEmbedding

from ..core.config import settings


def get_embedding(text: str) -> List[float]:
    """
    Generate embeddings for text using OpenAI via LlamaIndex.

    Args:
        text (str): Input text.

    Returns:
        List[float]: Embedding vector as a list of floats.
    """
    try:
        embed_model = OpenAIEmbedding(api_key=settings.openrouter_api_key)
        return embed_model.get_text_embedding(text)
    except Exception as e:
        raise Exception(f"Failed to generate embedding: {e!s}")
