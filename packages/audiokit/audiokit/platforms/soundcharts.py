"""Soundcharts platform processor for artist analytics"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import Field

from .base import (
    PlatformProcessor,
    ResponseModel,
)
from ..models import ArtistData
from ..logger import Logger
from ..processor import DocumentProcessor
from config import cfg


class SoundchartsMetrics(BaseModel):
    """Standardized metrics model for Soundcharts data"""

    platform: str
    metric_type: str
    value: float
    timestamp: datetime


class SoundchartsResponse(ResponseModel):
    """Standardized response model for Soundcharts data"""

    class Config:
        """Pydantic config"""

        json_schema_extra = {
            "example": {
                "platform": "soundcharts",
                "timestamp": "2025-02-15T12:00:00Z",
                "raw_data": {
                    "current_stats": {
                        "spotify": {
                            "followers": 1000000,
                            "monthly_listeners": 5000000,
                            "popularity": 75,
                        },
                        "instagram": {
                            "followers": 500000,
                            "posts": 1200,
                        },
                        "youtube": {
                            "subscribers": 750000,
                            "views": 25000000,
                        },
                    },
                    "audience": {
                        "age_distribution": {
                            "18-24": 0.25,
                            "25-34": 0.45,
                            "35-44": 0.20,
                            "45+": 0.10,
                        },
                        "gender_distribution": {
                            "male": 0.48,
                            "female": 0.51,
                            "other": 0.01,
                        },
                        "top_countries": [
                            {"country": "US", "share": 0.35},
                            {"country": "UK", "share": 0.15},
                            {"country": "DE", "share": 0.10},
                        ],
                    },
                    "similar_artists": [
                        {
                            "id": "artist1",
                            "name": "Similar Artist 1",
                            "genres": ["electronic", "house"],
                            "spotify_followers": 900000,
                        },
                        {
                            "id": "artist2",
                            "name": "Similar Artist 2",
                            "genres": ["electronic", "techno"],
                            "spotify_followers": 1200000,
                        },
                    ],
                },
                "cache_info": {
                    "hit": False,
                    "key": "platform:soundcharts:123",
                    "timestamp": "2025-02-15T12:00:00Z",
                },
            }
        }

    # Additional fields specific to Soundcharts
    current_stats: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Current statistics across different platforms",
    )
    audience: Dict[str, Any] = Field(
        default_factory=dict,
        description="Audience demographics and insights",
    )
    similar_artists: list[Dict[str, Any]] = Field(
        default_factory=list,
        description="Similar artists data",
    )


class SoundchartsProcessor(PlatformProcessor[SoundchartsResponse]):
    """Processor for Soundcharts platform data"""

    def __init__(self, artist_data: ArtistData):
        super().__init__(artist_data)
        self.base_url = "https://customer.api.soundcharts.com/api/v2"
        self.app_id = cfg.soundcharts.app_id
        self.api_key = cfg.soundcharts.api_key
        self.doc_processor = DocumentProcessor(artist_data.id)

    async def _get_auth_credentials(self) -> Dict[str, Any]:
        """Get Soundcharts authentication headers"""
        return {
            "x-app-id": self.app_id,
            "x-api-key": self.api_key,
        }

    async def _refresh_auth_token(self) -> None:
        """Not used - Soundcharts uses API key authentication"""
        raise NotImplementedError("Soundcharts does not support token refresh")

    def _extract_metrics(self, data: Dict[str, Any]) -> List[SoundchartsMetrics]:
        """Extract standardized metrics from raw data"""
        metrics = []
        timestamp = datetime.now()

        # Process platform-specific metrics
        for platform, stats in data.items():
            for metric_name, value in stats.items():
                if isinstance(value, (int, float)):
                    metrics.append(
                        SoundchartsMetrics(
                            platform=platform,
                            metric_type=metric_name,
                            value=float(value),
                            timestamp=timestamp,
                        )
                    )

        return metrics

    def transform_response(
        self, response: Dict[str, Any], cache_info: Optional[Dict[str, Any]] = None
    ) -> SoundchartsResponse:
        """Transform Soundcharts API response to standard format"""
        return SoundchartsResponse(
            platform="soundcharts",
            timestamp=datetime.now(),
            raw_data=response,
            cache_info=cache_info,
            current_stats=response.get("current_stats", {}),
            audience=response.get("audience", {}),
            similar_artists=response.get("similar_artists", []),
        )

    async def fetch_data(self) -> SoundchartsResponse:
        """Fetch artist data from Soundcharts"""
        try:
            # Get auth headers
            headers = await self._get_auth_credentials()

            # Fetch current stats
            current_stats = await self._make_request(
                "GET",
                f"{self.base_url}/artist/{self.artist_data.soundcharts_id}/current-stats",
                headers=headers,
                auth_required=False,  # We handle auth headers manually
            )

            # Fetch audience insights
            audience = await self._make_request(
                "GET",
                f"{self.base_url}/artist/{self.artist_data.soundcharts_id}/audience",
                headers=headers,
                auth_required=False,
            )

            # Fetch similar artists
            similar_artists = await self._make_request(
                "GET",
                f"{self.base_url}/artist/{self.artist_data.soundcharts_id}/similar",
                headers=headers,
                auth_required=False,
            )

            # Combine all data
            combined_data = {
                "current_stats": current_stats.get("object", {}),
                "audience": audience.get("object", {}),
                "similar_artists": similar_artists.get("items", []),
            }

            return self.transform_response(combined_data)

        except Exception as e:
            Logger.error(f"Failed to fetch Soundcharts data: {str(e)}")
            raise

    async def process(self) -> SoundchartsResponse:
        """Process and store Soundcharts data"""
        try:
            # Fetch data
            response = await self.fetch_data()
            timestamp = datetime.now().isoformat()

            # Process current stats as analytics
            if response.current_stats:
                # Extract and store metrics
                metrics = self._extract_metrics(response.current_stats)
                await self.doc_processor.process_analytics(
                    platform="soundcharts",
                    analytics_data={
                        "metrics": [m.model_dump() for m in metrics],
                        "timestamp": timestamp,
                        "raw_data": response.current_stats,
                    },
                )

            # Process audience data
            if response.audience:
                await self.doc_processor.process_analytics(
                    platform="soundcharts_audience",
                    analytics_data={
                        "demographics": response.audience,
                        "timestamp": timestamp,
                    },
                )

            # Process similar artists
            if response.similar_artists:
                await self.doc_processor.process_analytics(
                    platform="soundcharts_similar",
                    analytics_data={
                        "similar_artists": response.similar_artists,
                        "timestamp": timestamp,
                    },
                )

            # Store raw response for historical tracking
            await self.doc_processor.process_analytics(
                platform="soundcharts_raw",
                analytics_data={
                    "raw_data": response.raw_data,
                    "timestamp": timestamp,
                },
            )

            Logger.success(
                f"Processed Soundcharts data for artist {self.artist_data.id}"
            )
            return response

        except Exception as e:
            Logger.error(f"Failed to process Soundcharts data: {str(e)}")
            raise
