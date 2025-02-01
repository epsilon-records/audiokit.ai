"""Knowledge base implementation using LlamaIndex and Pinecone"""

from typing import Dict, List, Optional, Any, AsyncIterator, Union, TypeVar, Callable
from pydantic import BaseModel
import json
import hashlib
from datetime import timedelta
import asyncio
from functools import wraps
import random

from llama_index import VectorStoreIndex, Document, ServiceContext
from llama_index.vector_stores import PineconeVectorStore
from llama_index.schema import MetadataMode
from llama_index.postprocessor import SentenceTransformerRerank
from llama_index.prompts import PromptTemplate
from llama_index.query_engine import RetrieverQueryEngine
from pinecone import Pinecone
import redis.asyncio as redis
import httpx

from .logger import Logger
from config import cfg


T = TypeVar("T")


def with_retries(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    retryable_exceptions: tuple = (
        httpx.HTTPError,
        redis.RedisError,
        asyncio.TimeoutError,
        ConnectionError,
    ),
):
    """Retry decorator with exponential backoff"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            attempt = 0

            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)

                except retryable_exceptions as e:
                    attempt += 1
                    last_exception = e

                    if attempt == max_attempts:
                        Logger.error(
                            f"Max retry attempts ({max_attempts}) reached for {func.__name__}"
                        )
                        raise last_exception

                    # Calculate delay with jitter
                    delay = min(
                        base_delay * (2 ** (attempt - 1)) + random.random(), max_delay
                    )
                    Logger.warning(
                        f"Attempt {attempt} failed for {func.__name__}, retrying in {delay:.2f}s: {str(e)}"
                    )
                    await asyncio.sleep(delay)

                except Exception as e:
                    # Non-retryable exception
                    Logger.error(f"Non-retryable error in {func.__name__}: {str(e)}")
                    raise

            raise last_exception

        return wrapper

    return decorator


class DocumentMetadata(BaseModel):
    """Metadata for documents in the knowledge base"""

    artist_id: str
    doc_type: str
    source: str
    timestamp: str
    language: str = "en"
    version: str = "1.0"


class QueryCache:
    """Cache for query results"""

    def __init__(self, artist_id: str):
        self.artist_id = artist_id
        self.redis = redis.from_url(cfg.redis.url)
        self.default_ttl = timedelta(hours=24)

    def _get_cache_key(self, query: str, filters: Dict[str, Any]) -> str:
        """Generate cache key from query and filters"""
        cache_data = {"artist_id": self.artist_id, "query": query, "filters": filters}
        cache_str = json.dumps(cache_data, sort_keys=True)
        return f"kb:query:{hashlib.sha256(cache_str.encode()).hexdigest()}"

    async def get(
        self, query: str, filters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get cached query result"""
        try:
            key = self._get_cache_key(query, filters)
            cached = await self.redis.get(key)
            if cached:
                Logger.info("Cache hit for query")
                return json.loads(cached)
            return None
        except Exception as e:
            Logger.warning(f"Cache get failed: {str(e)}")
            return None

    async def set(
        self,
        query: str,
        filters: Dict[str, Any],
        result: Dict[str, Any],
        ttl: Optional[timedelta] = None,
    ):
        """Cache query result"""
        try:
            key = self._get_cache_key(query, filters)
            ttl = ttl or self.default_ttl
            await self.redis.setex(key, int(ttl.total_seconds()), json.dumps(result))
            Logger.info("Cached query result")
        except Exception as e:
            Logger.warning(f"Cache set failed: {str(e)}")

    async def close(self):
        """Close Redis connection"""
        await self.redis.close()


class KnowledgeBase:
    """Artist knowledge base using Pinecone vector store"""

    def __init__(self, artist_id: str):
        self.artist_id = artist_id
        self.namespace = f"artist_{artist_id}"
        self.cache = QueryCache(artist_id)
        self._init_pinecone()

        # Initialize service context with embedding model
        self.service_context = ServiceContext.from_defaults(
            embed_model=cfg.models.embedding, chunk_size=512, chunk_overlap=50
        )

        # Initialize reranker
        self.reranker = SentenceTransformerRerank(model=cfg.models.reranking, top_n=5)

        # Query transformation prompt
        self.query_transform_prompt = PromptTemplate(
            """Given the original query: {query}
            Generate an improved version that will help retrieve relevant information about the artist.
            Focus on key aspects like musical style, achievements, and unique characteristics.
            
            Improved query:"""
        )

    @with_retries()
    async def _init_pinecone(self):
        """Initialize Pinecone connection with retries"""
        try:
            pc = Pinecone(api_key=cfg.pinecone.api_key)
            pinecone_index = pc.Index(cfg.pinecone.index_name)

            self.vector_store = PineconeVectorStore(
                pinecone_index=pinecone_index,
                namespace=self.namespace,
                metadata_config={
                    "indexed": ["artist_id", "doc_type", "source", "language"]
                },
            )

            Logger.info(f"Initialized Pinecone for artist {self.artist_id}")
        except Exception as e:
            Logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise

    @with_retries()
    async def store_document(self, content: str, metadata: DocumentMetadata) -> str:
        """Store a single document in the knowledge base with retries"""
        try:
            # Create LlamaIndex document
            doc = Document(
                text=content,
                metadata=metadata.model_dump(),
                excluded_embed_metadata_keys=["timestamp", "version"],
                excluded_llm_metadata_keys=["timestamp", "version"],
                metadata_mode=MetadataMode.ALL,
            )

            # Create or update index
            index = VectorStoreIndex.from_documents(
                [doc],
                vector_store=self.vector_store,
                embed_model=cfg.models.embedding,
                show_progress=True,
            )

            Logger.success(
                f"Stored document type {metadata.doc_type} for artist {self.artist_id}"
            )
            return doc.doc_id

        except Exception as e:
            Logger.error(f"Failed to store document: {str(e)}")
            raise

    @with_retries(max_attempts=2)  # Fewer retries for query transformation
    async def _transform_query(self, query: str) -> str:
        """Transform query for better retrieval with retries"""
        try:
            messages = [
                {"role": "system", "content": "You are a query optimization expert."},
                {
                    "role": "user",
                    "content": self.query_transform_prompt.format(query=query),
                },
            ]

            async with OpenRouterClient(cfg.models.query_transform) as client:
                improved_query = await client.chat_completion(messages)
                Logger.info(f"Transformed query: {improved_query}")
                return improved_query.strip()

        except Exception as e:
            Logger.warning(f"Query transformation failed, using original: {str(e)}")
            return query

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cache.close()

    @with_retries()
    async def query(
        self,
        query: str,
        doc_types: Optional[List[str]] = None,
        source: Optional[str] = None,
        top_k: int = 5,
        stream: bool = False,
        use_cache: bool = True,
    ) -> Union[Dict[str, Any], AsyncIterator[str]]:
        """Query the knowledge base with filters, streaming support, and retries"""
        try:
            # Build metadata filter
            filters = {"artist_id": self.artist_id}
            if doc_types:
                filters["doc_type"] = {"$in": doc_types}
            if source:
                filters["source"] = source

            # Check cache for non-streaming queries
            if use_cache and not stream:
                cached_result = await self.cache.get(query, filters)
                if cached_result:
                    return cached_result

            # Transform query for better retrieval
            improved_query = await self._transform_query(query)

            # Create index with service context
            index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store, service_context=self.service_context
            )

            # Configure retriever with reranking
            retriever = index.as_retriever(
                filters=filters,
                similarity_top_k=top_k * 2,  # Retrieve more for reranking
            )

            # Create query engine with reranking
            query_engine = RetrieverQueryEngine.from_args(
                retriever=retriever,
                node_postprocessors=[self.reranker],
                streaming=stream,
                response_mode="tree_summarize",
            )

            if stream:
                # Return streaming response
                response = await query_engine.aquery(improved_query)
                async for text in response.async_response_gen():
                    yield text
            else:
                # Return complete response
                response = await query_engine.aquery(improved_query)
                result = {
                    "response": response.response,
                    "source_nodes": [
                        {
                            "content": node.node.text,
                            "metadata": node.node.metadata,
                            "score": node.score,
                        }
                        for node in response.source_nodes
                    ],
                }

                # Cache the result
                if use_cache:
                    await self.cache.set(query, filters, result)

                return result

        except Exception as e:
            Logger.error(f"Failed to query knowledge base: {str(e)}")
            raise

    @with_retries()
    async def delete_documents(
        self, doc_types: Optional[List[str]] = None, source: Optional[str] = None
    ):
        """Delete documents matching filters with retries"""
        try:
            # Build metadata filter
            filters = {"artist_id": self.artist_id}
            if doc_types:
                filters["doc_type"] = {"$in": doc_types}
            if source:
                filters["source"] = source

            # Delete matching documents
            self.vector_store.delete(filters)
            Logger.success(f"Deleted documents for artist {self.artist_id}")

        except Exception as e:
            Logger.error(f"Failed to delete documents: {str(e)}")
            raise
