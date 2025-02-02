"""Document processor for ingesting various types of artist data.

This module handles the processing and ingestion of various types of artist data
into the knowledge base, including:
- Core artist profile data
- Social media data
- Press coverage
- Analytics
- Performance history
- AI-generated content

Example:
    >>> processor = DocumentProcessor(artist_id="123")
    >>> await processor.process_artist_data(artist_data)
"""

from datetime import datetime
from typing import List, Dict, Any
import json

from audiokit.models import ArtistData
from audiokit.logger import Logger

from .ai.knowledge_base import KnowledgeBase, DocumentMetadata


class DocumentProcessor:
    """Processes and ingests artist documents into knowledge base.

    This class handles the processing and storage of various types of artist-related
    documents into a centralized knowledge base. It ensures proper metadata tagging
    and consistent storage format.

    Args:
        artist_id: Unique identifier for the artist

    Example:
        >>> processor = DocumentProcessor("artist123")
        >>> await processor.process_artist_data(artist_data)
    """

    def __init__(self, artist_id: str):
        """Initialize the document processor.

        Args:
            artist_id: Unique identifier for the artist
        """
        self.artist_id = artist_id
        self.knowledge_base = KnowledgeBase(artist_id)

    async def process_artist_data(self, artist_data: ArtistData) -> None:
        """Process core artist data.

        Args:
            artist_data: Core artist profile data

        Raises:
            ProcessingError: If processing fails
        """
        try:
            # Convert to structured format
            content = json.dumps(artist_data.model_dump(), indent=2)

            metadata = DocumentMetadata(
                artist_id=self.artist_id,
                doc_type="artist_profile",
                source="database",
                timestamp=datetime.now().isoformat(),
            )

            await self.knowledge_base.store_document(content, metadata)
            Logger.success(f"Processed core data for artist {self.artist_id}")

        except Exception as e:
            Logger.error(f"Failed to process artist data: {str(e)}")
            raise

    async def process_social_media(self, platform: str, data: Dict[str, Any]) -> None:
        """Process social media data.

        Args:
            platform: Name of the social media platform
            data: Platform-specific data

        Raises:
            ProcessingError: If processing fails
        """
        try:
            content = json.dumps(data, indent=2)

            metadata = DocumentMetadata(
                artist_id=self.artist_id,
                doc_type="social_media",
                source=platform,
                timestamp=datetime.now().isoformat(),
            )

            await self.knowledge_base.store_document(content, metadata)
            Logger.success(f"Processed {platform} data for artist {self.artist_id}")

        except Exception as e:
            Logger.error(f"Failed to process social media data: {str(e)}")
            raise

    async def process_press(self, press_data: Dict[str, Any]) -> None:
        """Process press releases and articles.

        Args:
            press_data: Press coverage data

        Raises:
            ProcessingError: If processing fails
        """
        try:
            content = json.dumps(press_data, indent=2)

            metadata = DocumentMetadata(
                artist_id=self.artist_id,
                doc_type="press",
                source=press_data.get("source", "unknown"),
                timestamp=datetime.now().isoformat(),
            )

            await self.knowledge_base.store_document(content, metadata)
            Logger.success(f"Processed press data for artist {self.artist_id}")

        except Exception as e:
            Logger.error(f"Failed to process press data: {str(e)}")
            raise

    async def process_analytics(
        self, platform: str, analytics_data: Dict[str, Any]
    ) -> None:
        """Process streaming and social media analytics.

        Args:
            platform: Platform name (e.g., "spotify", "youtube")
            analytics_data: Platform-specific analytics data

        Raises:
            ProcessingError: If processing fails
        """
        try:
            content = json.dumps(analytics_data, indent=2)

            metadata = DocumentMetadata(
                artist_id=self.artist_id,
                doc_type="analytics",
                source=platform,
                timestamp=datetime.now().isoformat(),
            )

            await self.knowledge_base.store_document(content, metadata)
            Logger.success(
                f"Processed {platform} analytics for artist {self.artist_id}"
            )

        except Exception as e:
            Logger.error(f"Failed to process analytics data: {str(e)}")
            raise

    async def process_performance_history(
        self, performances: List[Dict[str, Any]]
    ) -> None:
        """Process performance and tour history.

        Args:
            performances: List of performance data

        Raises:
            ProcessingError: If processing fails
        """
        try:
            content = json.dumps(performances, indent=2)

            metadata = DocumentMetadata(
                artist_id=self.artist_id,
                doc_type="performances",
                source="events_db",
                timestamp=datetime.now().isoformat(),
            )

            await self.knowledge_base.store_document(content, metadata)
            Logger.success(f"Processed performance history for artist {self.artist_id}")

        except Exception as e:
            Logger.error(f"Failed to process performance history: {str(e)}")
            raise

    async def process_generated_content(self, content_type: str, content: str) -> None:
        """Process AI-generated content like EPKs and reports.

        Args:
            content_type: Type of generated content (e.g., "epk", "report")
            content: The generated content

        Raises:
            ProcessingError: If processing fails
        """
        try:
            metadata = DocumentMetadata(
                artist_id=self.artist_id,
                doc_type=content_type,
                source="ai_generated",
                timestamp=datetime.now().isoformat(),
            )

            await self.knowledge_base.store_document(content, metadata)
            Logger.success(f"Processed {content_type} for artist {self.artist_id}")

        except Exception as e:
            Logger.error(f"Failed to process generated content: {str(e)}")
            raise
