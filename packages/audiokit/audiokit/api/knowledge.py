"""FastAPI endpoints for artist brain - knowledge base and document management

This module provides endpoints for:
1. Querying the knowledge base
2. Managing documents (upload, delete, list)
3. Retrieving metadata and statistics
4. Managing data sources and document types

All endpoints require artist authentication and operate within the artist's namespace.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..knowledge_base import KnowledgeBase, DocumentMetadata
from ..logger import Logger
from ..models import ArtistData
from ..auth import get_current_artist


router = APIRouter(prefix="/brain", tags=["brain"])


class QueryRequest(BaseModel):
    """Knowledge base query request"""

    query: str = Field(..., description="The query to run against the knowledge base")
    doc_types: Optional[List[str]] = Field(None, description="Filter by document types")
    source: Optional[str] = Field(None, description="Filter by source")
    top_k: int = Field(5, description="Number of results to return", ge=1, le=20)
    stream: bool = Field(False, description="Whether to stream the response")
    use_cache: bool = Field(True, description="Whether to use cached results")

    class Config:
        schema_extra = {
            "example": {
                "query": "What are the artist's recent achievements?",
                "doc_types": ["news", "social_media"],
                "top_k": 5,
                "stream": False,
                "use_cache": True,
            }
        }


class QueryResponse(BaseModel):
    """Knowledge base query response"""

    response: str = Field(..., description="Generated response from the knowledge base")
    source_nodes: List[dict] = Field(
        ..., description="Source documents used for the response"
    )


class DocumentUpload(BaseModel):
    """Document upload metadata"""

    doc_type: str = Field(
        ..., description="Type of document (e.g., news, social_media)"
    )
    source: str = Field(..., description="Source of the document")
    language: str = Field("en", description="Document language")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        schema_extra = {
            "example": {
                "doc_type": "news",
                "source": "music_blog",
                "language": "en",
                "metadata": {
                    "url": "https://example.com/article",
                    "author": "John Doe",
                    "published_date": "2024-02-15",
                },
            }
        }


class DocumentStats(BaseModel):
    """Document statistics"""

    total_documents: int = Field(..., description="Total number of documents")
    by_type: Dict[str, int] = Field(..., description="Document count by type")
    by_source: Dict[str, int] = Field(..., description="Document count by source")
    by_language: Dict[str, int] = Field(..., description="Document count by language")
    last_updated: datetime = Field(..., description="Last document update timestamp")


@router.post(
    "/query",
    response_model=QueryResponse,
    description="""
Query the knowledge base with optional filters and streaming support.
Returns either a complete response or streams the response as events.
""",
)
async def query_knowledge_base(
    request: QueryRequest, artist: ArtistData = Depends(get_current_artist)
) -> QueryResponse:
    """Query the knowledge base"""
    try:
        async with KnowledgeBase(artist.id) as kb:
            if request.stream:
                return StreamingResponse(
                    kb.query(
                        query=request.query,
                        doc_types=request.doc_types,
                        source=request.source,
                        top_k=request.top_k,
                        stream=True,
                        use_cache=request.use_cache,
                    ),
                    media_type="text/event-stream",
                )
            else:
                result = await kb.query(
                    query=request.query,
                    doc_types=request.doc_types,
                    source=request.source,
                    top_k=request.top_k,
                    stream=False,
                    use_cache=request.use_cache,
                )
                return QueryResponse(**result)

    except Exception as e:
        Logger.error(f"Knowledge base query failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Knowledge base query failed: {str(e)}"
        )


@router.post("/documents", description="Upload a document to the knowledge base")
async def upload_document(
    metadata: DocumentUpload,
    file: UploadFile = File(...),
    artist: ArtistData = Depends(get_current_artist),
) -> Dict[str, str]:
    """Upload a document to the knowledge base"""
    try:
        content = await file.read()
        content_str = content.decode()

        async with KnowledgeBase(artist.id) as kb:
            doc_metadata = DocumentMetadata(
                artist_id=artist.id,
                doc_type=metadata.doc_type,
                source=metadata.source,
                language=metadata.language,
                timestamp=datetime.now().isoformat(),
                **metadata.metadata or {},
            )

            doc_id = await kb.store_document(content_str, doc_metadata)
            return {"doc_id": doc_id, "message": "Document uploaded successfully"}

    except Exception as e:
        Logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")


@router.delete("/documents", description="Delete documents matching the filters")
async def delete_documents(
    doc_types: Optional[List[str]] = Query(None),
    source: Optional[str] = Query(None),
    artist: ArtistData = Depends(get_current_artist),
) -> Dict[str, str]:
    """Delete documents matching the filters"""
    try:
        async with KnowledgeBase(artist.id) as kb:
            await kb.delete_documents(doc_types=doc_types, source=source)
            return {"message": "Documents deleted successfully"}

    except Exception as e:
        Logger.error(f"Document deletion failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Document deletion failed: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=DocumentStats,
    description="""
Get statistics about the documents in the knowledge base.
Includes counts by type, source, and language.
""",
)
async def get_stats(artist: ArtistData = Depends(get_current_artist)) -> DocumentStats:
    """Get document statistics"""
    try:
        async with KnowledgeBase(artist.id) as kb:
            result = await kb.query(
                query="",
                top_k=1000,
                use_cache=True,
            )

            stats = {
                "total_documents": len(result["source_nodes"]),
                "by_type": {},
                "by_source": {},
                "by_language": {},
                "last_updated": datetime.now(),  # TODO: Get from metadata
            }

            for node in result["source_nodes"]:
                metadata = node["metadata"]

                # Count by type
                doc_type = metadata["doc_type"]
                stats["by_type"][doc_type] = stats["by_type"].get(doc_type, 0) + 1

                # Count by source
                source = metadata["source"]
                stats["by_source"][source] = stats["by_source"].get(source, 0) + 1

                # Count by language
                lang = metadata.get("language", "en")
                stats["by_language"][lang] = stats["by_language"].get(lang, 0) + 1

            return DocumentStats(**stats)

    except Exception as e:
        Logger.error(f"Failed to get stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get(
    "/doc_types",
    response_model=List[str],
    description="""
List all document types available in the knowledge base.
Returns a sorted list of unique document types.
""",
)
async def list_doc_types(artist: ArtistData = Depends(get_current_artist)) -> List[str]:
    """List available document types"""
    try:
        async with KnowledgeBase(artist.id) as kb:
            result = await kb.query(
                query="",
                top_k=1000,
                use_cache=True,
            )

            doc_types = {
                node["metadata"]["doc_type"] for node in result["source_nodes"]
            }
            return sorted(list(doc_types))

    except Exception as e:
        Logger.error(f"Failed to list doc types: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list doc types: {str(e)}"
        )


@router.get(
    "/sources",
    response_model=List[str],
    description="""
List all sources available in the knowledge base.
Returns a sorted list of unique sources.
""",
)
async def list_sources(artist: ArtistData = Depends(get_current_artist)) -> List[str]:
    """List available sources"""
    try:
        async with KnowledgeBase(artist.id) as kb:
            result = await kb.query(
                query="",
                top_k=1000,
                use_cache=True,
            )

            sources = {node["metadata"]["source"] for node in result["source_nodes"]}
            return sorted(list(sources))

    except Exception as e:
        Logger.error(f"Failed to list sources: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list sources: {str(e)}")
