from typing import List

import numpy as np


def pad_embedding(embedding: List[float], target_dim: int = 1024) -> List[float]:
    """
    Pad or truncate embedding to target dimension.
    Uses numpy for efficient array operations.
    """
    # Convert to numpy array for easier manipulation
    arr = np.array(embedding, dtype=np.float32)

    # Get current dimension
    curr_dim = arr.shape[0]

    if curr_dim == target_dim:
        return arr.tolist()

    if curr_dim > target_dim:
        # Truncate to target dimension
        return arr[:target_dim].tolist()

    # Pad with zeros
    return np.pad(arr, (0, target_dim - curr_dim)).tolist()
