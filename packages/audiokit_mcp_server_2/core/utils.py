import uuid


def generate_unique_id() -> str:
    """
    Generate a unique identifier as a string.
    """
    return str(uuid.uuid4())


def safe_dict_get(d: dict, key: str, default=None):
    """
    Safely get a value from a dictionary.

    Args:
        d (dict): The dictionary.
        key (str): Key to search.
        default: Default value if key not found.

    Returns:
        The value if present, else default.
    """
    return d.get(key, default)
