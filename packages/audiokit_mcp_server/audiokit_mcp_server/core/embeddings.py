from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from audiokit_mcp_server.core.logger import logger


# Initialize model once as a global singleton
# all-MiniLM-L6-v2 is a good balance of speed and quality
model = SentenceTransformer("all-MiniLM-L6-v2")

# Target dimension for Pinecone index
TARGET_DIMENSIONS = 1024


async def get_embedding(text: str) -> List[float]:
    """Get embedding vector using Sentence Transformers with padding to 1024d"""
    try:
        # Get base embedding (384 dimensions)
        embedding = model.encode(text, convert_to_tensor=False)

        # Pad with zeros to match 1024 dimensions
        padded = np.pad(
            embedding,
            (0, TARGET_DIMENSIONS - len(embedding)),
            "constant",
            constant_values=0,
        )

        return padded.tolist()
    except Exception as e:
        logger.error(f"Failed to get embedding: {e!s}")
        raise
