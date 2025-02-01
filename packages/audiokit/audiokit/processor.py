"""Document processor for ingesting various types of artist data"""

from datetime import datetime
from typing import List, Dict, Any
import json

from .knowledge_base import KnowledgeBase, DocumentMetadata
from .models import ArtistData
from .logger import Logger


class DocumentProcessor:
    """Processes and ingests artist documents into knowledge base"""

    def __init__(self, artist_id: str):
        self.artist_id = artist_id
        self.knowledge_base = KnowledgeBase(artist_id)

    async def process_artist_data(self, artist_data: ArtistData):
        """Process core artist data"""
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

    async def process_social_media(self, platform: str, data: Dict[str, Any]):
        """Process social media data"""
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

    async def process_press(self, press_data: Dict[str, Any]):
        """Process press releases and articles"""
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

    async def process_analytics(self, platform: str, analytics_data: Dict[str, Any]):
        """Process streaming and social media analytics"""
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

    async def process_performance_history(self, performances: List[Dict[str, Any]]):
        """Process performance and tour history"""
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

    async def process_generated_content(self, content_type: str, content: str):
        """Process AI-generated content like EPKs and reports"""
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
