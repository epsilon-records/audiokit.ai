def ingest_file(file_path: str) -> dict:
    """
    Ingest a generic file and return its content and metadata.

    Args:
        file_path (str): Path to the file.

    Returns:
        dict: Information about the ingested file.
    """
    try:
        with open(file_path) as f:
            content = f.read()
        status = "ingested"
    except Exception as e:
        content = ""
        status = f"error: {e}"
    return {"file_path": file_path, "content": content, "status": status}
