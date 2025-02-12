def run_query_pipeline(query: str) -> dict:
    """
    Run the query pipeline to process natural language queries.
    It includes LLM processing and a vector search.

    Args:
        query (str): The natural language query.

    Returns:
        dict: Aggregated query and search results.
    """
    from ..handlers.query import query_handler, search_handler

    # Process the query.
    query_result = query_handler.process_query(query)

    # Generate an embedding for the query.
    from ..services.embedding_service import get_embedding

    query_embedding = get_embedding(query)

    # Perform a vector similarity search.
    search_result = search_handler.perform_search(query_embedding)

    return {
        "query_result": query_result,
        "search_result": search_result,
    }
