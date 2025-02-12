from typing import Dict, List

from pydantic import BaseModel


class Query(BaseModel):
    """
    Model representing a search query.
    """

    query_text: str
    filters: Dict = {}
    limit: int = 10


class QueryResult(BaseModel):
    """
    Model representing a query result.
    """

    items: List[dict]
