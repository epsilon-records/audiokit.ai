import json
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from fastapi import HTTPException
from pinecone import Pinecone
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)
from scipy import stats

from audiokit_mcp_server.core.config import settings
from audiokit_mcp_server.core.embeddings import get_embedding
from audiokit_mcp_server.core.llm import call_llm  # Update import
from audiokit_mcp_server.core.logger import logger
from audiokit_mcp_server.handlers.soundcharts_client import SoundchartsClient
from audiokit_mcp_server.models.spotify_analytics_request import SpotifyAnalyticsRequest


class AnalyticsQuery(BaseModel):
    query: str  # Natural language query about analytics
    data_types: List[str] = ["users", "conversions", "formats"]  # What data to include
    time_range: Optional[str] = "30d"  # Time range to analyze
    context_filter: Optional[Dict[str, str]] = None  # Filter context by metadata
    min_relevance: float = Field(0.7, ge=0, le=1.0)  # Minimum relevance score


class AnalyticsInsight(BaseModel):
    """Model for analytics insights"""

    insight: str
    report_url: str
    data_snapshot: Dict
    timestamp: datetime
    reference_id: Optional[str] = None  # Vector store reference ID


class PineconeClient:
    """Pinecone client wrapper"""

    def __init__(self):
        # Initialize Pinecone with new API
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)

        # Use existing audiokit-brain index
        self.index = self.pc.Index("audiokit-brain")

    async def store_insight(
        self,
        insight: AnalyticsInsight,
        data_types: List[str],
        time_range: str,
    ) -> str:
        """Store insight in Pinecone"""
        try:
            # Extract only essential data for metadata
            essential_data = {
                "metadata": insight.data_snapshot.get("metadata", {}),
                "current_stats": insight.data_snapshot.get("current_stats", {}),
                # Add other critical fields as needed
            }

            # Create Pinecone metadata with reduced data
            metadata = {
                "query": insight.insight or "",  # Use empty string if query is None
                "insight": insight.insight,
                "data_snapshot": json.dumps(
                    essential_data,
                ),  # Store only essential data
                "timestamp": insight.timestamp.isoformat(),
                "data_types": ",".join(data_types),
                "time_range": time_range,
            }

            # Log metadata size for debugging
            metadata_size = len(json.dumps(metadata).encode("utf-8"))
            logger.debug(f"Metadata size: {metadata_size / 1024:.2f}KB")

            if metadata_size > 40000:  # Pinecone's limit is 40KB
                logger.warning(
                    "Metadata exceeds Pinecone limit, truncating data_snapshot",
                )
                # Further reduce data if still too large
                metadata["data_snapshot"] = json.dumps(
                    {
                        "metadata": essential_data.get("metadata", {}),
                        "stats_summary": "Data truncated due to size limits",
                    },
                )

            # Convert insight to vector
            vector = await self.get_embedding(insight.insight)

            # Generate vector ID
            vector_id = f"insight_{datetime.utcnow().timestamp()}"

            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(vector_id, vector, metadata)],
            )

            return vector_id

        except Exception as e:
            logger.error(f"Failed to store insight: {e!s}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store insight: {e!s}",
            )

    async def get_related_insights(
        self,
        query: str,
        data_types: List[str],
        limit: int = 5,
    ) -> List[Dict]:
        """Get related insights using vector similarity"""
        try:
            # Convert query to vector
            query_vector = await self.get_embedding(query)

            # Search Pinecone
            results = self.index.query(
                vector=query_vector,
                filter={"data_types": {"$in": data_types}},
                top_k=limit,
                include_metadata=True,
            )

            return [
                {
                    "insight": match.metadata["insight"],
                    "score": match.score,
                    "timestamp": match.metadata["timestamp"],
                }
                for match in results.matches
            ]

        except Exception as e:
            logger.error(f"Failed to get related insights: {e!s}")
            return []

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector using OpenAI"""
        return await get_embedding(text)


# Initialize clients
pinecone_client = PineconeClient()
soundcharts_client = SoundchartsClient()


async def fetch_analytics_data(data_types: List[str], time_range: str) -> Dict:
    """Fetch analytics data from your data source"""
    # This would be replaced with your actual data fetching logic
    # Could be REST API call, database query, etc.

    sample_data = {
        "users": {
            "total": 1500,
            "active": 750,
            "new_this_period": 123,
        },
        "conversions": {
            "total": 5000,
            "successful": 4850,
            "failed": 150,
            "average_duration": 45.2,
        },
        "formats": {
            "wav": 1200,
            "mp3": 2500,
            "flac": 800,
            "aac": 500,
        },
    }

    return {k: v for k, v in sample_data.items() if k in data_types}


async def store_insight(
    insight: AnalyticsInsight,
    data_types: List[str],
    time_range: str,
) -> str:
    """Store analytics insight in Pinecone"""
    try:
        # Extract only essential data for metadata
        essential_data = {
            "metadata": insight.data_snapshot.get("metadata", {}),
            "current_stats": insight.data_snapshot.get("current_stats", {}),
        }

        # Create Pinecone metadata with reduced data
        metadata = {
            "query": insight.insight or "",  # Use empty string if query is None
            "insight": insight.insight,
            "data_snapshot": json.dumps(essential_data),
            "timestamp": insight.timestamp.isoformat(),
            "data_types": ",".join(data_types),
            "time_range": time_range,
        }

        # Log metadata size for debugging
        metadata_size = len(json.dumps(metadata).encode("utf-8"))
        logger.debug(f"Metadata size: {metadata_size / 1024:.2f}KB")

        if metadata_size > 40000:  # Pinecone's limit is 40KB
            logger.warning("Metadata exceeds Pinecone limit, truncating data_snapshot")
            # Further reduce data if still too large
            metadata["data_snapshot"] = json.dumps(
                {
                    "metadata": essential_data.get("metadata", {}),
                    "stats_summary": "Data truncated due to size limits",
                },
            )

        # Convert insight to vector
        vector = await pinecone_client.get_embedding(insight.insight)

        # Generate vector ID
        vector_id = f"insight_{datetime.utcnow().timestamp()}"

        # Upsert to Pinecone
        pinecone_client.index.upsert(
            vectors=[(vector_id, vector, metadata)],
        )

        return vector_id

    except Exception as e:
        logger.error(f"Failed to store insight: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to store insight: {e!s}")


class ContextConfig:
    MAX_INSIGHTS = 10
    MIN_SIMILARITY = 0.7
    TIME_WEIGHTS = {
        "24h": 1.0,
        "7d": 0.9,
        "30d": 0.8,
        "90d": 0.7,
        "older": 0.6,
    }


async def get_time_weighted_insights(
    data_types: List[str],
    min_relevance: float = ContextConfig.MIN_SIMILARITY,
    limit: int = ContextConfig.MAX_INSIGHTS,
) -> List[Dict]:
    """Get time-weighted related insights from Pinecone"""
    try:
        # Get related insights from Pinecone
        related_insights = await pinecone_client.get_related_insights(
            query="",  # Empty query since we're just getting recent insights
            data_types=data_types,
            limit=limit,
        )

        # Add time weights and sort by combined relevance
        weighted_insights = []
        for insight in related_insights:
            # Calculate age and get time weight
            age = datetime.utcnow() - datetime.fromisoformat(insight["timestamp"])

            if age <= timedelta(hours=24):
                time_weight = ContextConfig.TIME_WEIGHTS["24h"]
            elif age <= timedelta(days=7):
                time_weight = ContextConfig.TIME_WEIGHTS["7d"]
            elif age <= timedelta(days=30):
                time_weight = ContextConfig.TIME_WEIGHTS["30d"]
            elif age <= timedelta(days=90):
                time_weight = ContextConfig.TIME_WEIGHTS["90d"]
            else:
                time_weight = ContextConfig.TIME_WEIGHTS["older"]

            # Calculate combined relevance score
            score = insight["score"]
            combined_score = score * time_weight

            # Add metadata for context generation
            weighted_insights.append(
                {
                    **insight,
                    "age_days": age.days,
                    "relevance_score": combined_score,
                },
            )

        # Sort by combined relevance score
        weighted_insights.sort(key=lambda x: x["relevance_score"], reverse=True)

        return weighted_insights[:limit]

    except Exception as e:
        logger.warning(f"Error fetching related insights: {e!s}")
        return []


class OpenRouterConfig:
    """Configuration for OpenRouter API"""

    API_KEY = os.getenv("OPENROUTER_API_KEY")
    API_BASE = "https://openrouter.ai/api/v1"
    MODEL = "anthropic/claude-3.5-sonnet"

    @classmethod
    def get_headers(cls):
        return {
            "Authorization": f"Bearer {cls.API_KEY}",
            "HTTP-Referer": "https://audiokit.io",  # Replace with your domain
            "X-Title": "AudioKit Analytics",  # Your app name
        }


async def generate_insight(query: str, data: Dict, related_insights: List[Dict]) -> str:
    """Generate natural language insights using LLM with context"""
    # Build context sections
    recent_context = []
    historical_context = []

    for insight in related_insights:
        context_entry = (
            f"Previous insight ({insight['timestamp']}, "
            f"relevance: {insight['relevance_score']:.2f}): "
            f"{insight['insight']}"
        )

        if insight["age_days"] <= 30:
            recent_context.append(context_entry)
        else:
            historical_context.append(context_entry)

    prompt = f"""
    Recent Context (Last 30 days):
    {chr(10).join(recent_context) if recent_context else "No recent insights available"}
    
    Historical Context:
    {chr(10).join(historical_context) if historical_context else "No historical insights available"}
    
    Current Analytics Data: {json.dumps(data, indent=2)}
    User Query: {query}
    
    Please analyze this data and provide insights about {query}.
    Consider both recent and historical context when relevant.
    Focus on key trends, changes from historical patterns, and actionable insights.
    If there are conflicting trends between recent and historical data, highlight these changes.
    
    Format your response in clear, concise paragraphs. Include:
    1. Key findings
    2. Notable trends or changes
    3. Actionable recommendations
    4. Areas that need attention
    """

    return await call_llm(prompt)


async def analyze_spotify_uri(request: SpotifyAnalyticsRequest) -> Dict:
    """Analyze artist data from Spotify URI"""
    try:
        logger.info(f"Starting analysis for Spotify URI: {request.spotify_uri}")

        # Extract artist ID from Spotify URI
        spotify_id = request.spotify_uri.split(":")[-1]
        logger.debug(f"Extracted Spotify ID: {spotify_id}")

        # Get Soundcharts artist ID
        artist_id = await soundcharts_client.get_artist_by_spotify_uri(spotify_id)
        logger.debug(f"Got Soundcharts artist ID: {artist_id}")

        if not artist_id:
            raise HTTPException(status_code=404, detail="Artist not found")

        # Get artist data
        artist_data = await soundcharts_client.get_artist_data(artist_id)

        # Get related insights
        try:
            related_insights = await get_time_weighted_insights(
                data_types=["artist"],
            )
        except Exception as e:
            logger.warning(f"Failed to get related insights: {e!s}")
            related_insights = []

        # Generate insight
        insight_text, report_url = await soundcharts_client.generate_insight(
            artist_data,
            related_insights,
        )

        # Create and store insight
        analytics_insight = AnalyticsInsight(
            insight=insight_text,
            report_url=report_url,
            data_snapshot=artist_data,
            timestamp=datetime.utcnow(),
        )

        # Store insight and get reference ID
        try:
            reference_id = await store_insight(
                analytics_insight,
                ["artist"],
                "all",
            )
        except Exception as e:
            logger.error(f"Failed to store insight: {e!s}")
            reference_id = None

        # Update insight with reference ID
        analytics_insight.reference_id = reference_id

        return {
            "insight": insight_text,
            "report_url": report_url,
            "reference_id": reference_id,
            "timestamp": analytics_insight.timestamp.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze Spotify URI: {e!s}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e!s}")


class Platform(str, Enum):
    """Supported platforms from Soundcharts"""

    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    DEEZER = "deezer"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"


class ArtistMetadata(BaseModel):
    """Artist metadata from /artist/metadata"""

    id: str
    name: str
    isni: Optional[str]
    platforms: Dict[Platform, str] = Field(
        description="Platform-specific IDs",
        example={
            "spotify": "6eUKZXaKkcviH0Ku9w2n3V",
            "apple_music": "123456789",
        },
    )
    avatar_url: Optional[str]
    genres: List[str]
    is_verified: Dict[Platform, bool]
    links: Dict[str, str]


class ArtistCurrentStats(BaseModel):
    """Current statistics from /artist/current-stats"""

    spotify: Optional[Dict[str, int]] = Field(
        description="Spotify current stats",
        example={
            "followers": 1234567,
            "monthly_listeners": 789012,
            "popularity": 85,
        },
    )
    youtube: Optional[Dict[str, int]] = Field(
        example={
            "subscribers": 1000000,
            "total_views": 50000000,
        },
    )
    instagram: Optional[Dict[str, int]] = Field(
        example={
            "followers": 500000,
            "posts": 1234,
        },
    )
    tiktok: Optional[Dict[str, int]] = Field(
        example={
            "followers": 750000,
            "likes": 5000000,
            "videos": 100,
        },
    )


class ArtistAudienceMetrics(BaseModel):
    """Detailed audience metrics from /artist/audience"""

    spotify: Optional[Dict[str, Dict]] = Field(
        description="Spotify audience metrics",
        example={
            "followers": {
                "total": 1234567,
                "daily_diff": 123,
                "weekly_diff": 856,
            },
            "monthly_listeners": {
                "total": 789012,
                "daily_diff": 1234,
                "weekly_diff": 8567,
            },
            "popularity": {
                "current": 85,
                "daily_diff": 1,
                "weekly_diff": 3,
            },
        },
    )
    youtube: Optional[Dict[str, Dict]] = Field(
        description="YouTube metrics with historical changes",
    )
    instagram: Optional[Dict[str, Dict]]
    tiktok: Optional[Dict[str, Dict]]


class ArtistStreamingMetrics(BaseModel):
    """Streaming metrics from /artist/streaming-audience"""

    spotify: Optional[Dict[str, Dict]] = Field(
        example={
            "monthly_listeners": {
                "total": 789012,
                "top_countries": {
                    "US": 234567,
                    "GB": 123456,
                    "DE": 98765,
                },
            },
            "playlists": {
                "total_playlists": 5678,
                "total_playlist_reach": 10000000,
                "editorial_playlists": 123,
                "algorithmic_playlists": 456,
                "user_playlists": 5099,
            },
        },
    )
    apple_music: Optional[Dict[str, Dict]]
    youtube_music: Optional[Dict[str, Dict]]
    deezer: Optional[Dict[str, Dict]]


class ArtistSocialMetrics(BaseModel):
    """Social media metrics from /artist/social"""

    instagram: Optional[Dict[str, Dict]] = Field(
        example={
            "engagement": {
                "rate": 4.5,
                "total_interactions": 1000000,
            },
            "posts": {
                "total": 1234,
                "average_likes": 50000,
                "average_comments": 1000,
            },
            "audience_demographics": {
                "age_groups": {"18-24": 35, "25-34": 40},
                "gender": {"male": 48, "female": 52},
                "top_countries": {"US": 30, "UK": 15, "DE": 10},
            },
        },
    )
    tiktok: Optional[Dict[str, Dict]]
    youtube: Optional[Dict[str, Dict]]


class ArtistChartMetrics(BaseModel):
    """Chart performance from /artist/chart-entries"""

    entries: Dict[Platform, List[Dict]] = Field(
        example={
            "spotify": [
                {
                    "date": "2024-03-20",
                    "chart_name": "Top Artists",
                    "country": "US",
                    "position": 5,
                    "previous_position": 7,
                    "streams": 1234567,
                    "duration_ms": 86400000,  # 24h in ms
                },
            ],
        },
    )
    rankings: Dict[Platform, Dict[str, int]] = Field(
        description="Best rankings by platform/chart",
        example={
            "spotify": {
                "highest_position": 1,
                "weeks_in_top_10": 12,
                "total_weeks_charted": 52,
            },
        },
    )


class MetricValidation:
    """Validation rules for metrics"""

    MIN_FOLLOWERS = 0
    MAX_FOLLOWERS = 1_000_000_000
    MIN_STREAMS = 0
    MAX_STREAMS = 10_000_000_000
    MIN_ENGAGEMENT = 0.0
    MAX_ENGAGEMENT = 100.0
    VALID_CHART_POSITIONS = range(1, 201)
    MIN_DURATION_MS = 1000  # 1 second
    MAX_DURATION_MS = 7200000  # 2 hours

    @staticmethod
    def validate_percentage(value: float, field: str) -> float:
        if not 0 <= value <= 100:
            raise ValueError(f"{field} must be between 0 and 100")
        return value

    @staticmethod
    def validate_count(value: int, field: str, min_val: int, max_val: int) -> int:
        if not min_val <= value <= max_val:
            raise ValueError(f"{field} must be between {min_val} and {max_val}")
        return value


class TimeSeriesMetrics(BaseModel):
    """Time series data structure for metrics"""

    timestamp: datetime
    value: Union[int, float]
    change_percent: Optional[float]

    @field_validator("change_percent")
    def validate_change_percent(cls, v: float) -> float:
        if not -100 <= v <= 100:
            raise ValueError("change_percent must be between -100 and 100")
        return v


class MetricAggregation:
    """Methods for aggregating metrics"""

    @staticmethod
    def calculate_growth_rate(
        current: float,
        previous: float,
        time_delta: timedelta,
    ) -> float:
        """Calculate annualized growth rate"""
        if previous == 0:
            return 0.0
        days = time_delta.days or 1
        return ((current / previous) ** (365 / days) - 1) * 100

    @staticmethod
    def calculate_moving_average(
        data: List[TimeSeriesMetrics],
        window: int = 7,
    ) -> List[float]:
        """Calculate moving average of metrics"""
        df = pd.DataFrame(
            [(d.timestamp, d.value) for d in data],
            columns=["timestamp", "value"],
        ).set_index("timestamp")
        return df.rolling(window=window).mean()["value"].tolist()

    @staticmethod
    def detect_trend(data: List[TimeSeriesMetrics]) -> Dict[str, Any]:
        """Detect trend in time series data"""
        values = [d.value for d in data]
        z_score = np.abs(stats.zscore(values))

        return {
            "trend": np.polyfit(range(len(values)), values, 1)[0],
            "volatility": np.std(values),
            "outliers": [i for i, z in enumerate(z_score) if z > 3],
            "seasonality": bool(stats.periodogram(values)[0].max() > 2),
        }


class PlatformSpecificMetrics:
    """Platform-specific metric calculations"""

    @staticmethod
    def spotify_engagement_score(metrics: Dict) -> float:
        """Calculate Spotify engagement score"""
        monthly_listeners = metrics.get("monthly_listeners", 0)
        followers = metrics.get("followers", 0)

        if monthly_listeners == 0:
            return 0.0

        return (followers / monthly_listeners) * 100

    @staticmethod
    def youtube_engagement_rate(metrics: Dict) -> float:
        """Calculate YouTube engagement rate"""
        views = metrics.get("views", 0)
        likes = metrics.get("likes", 0)
        comments = metrics.get("comments", 0)

        if views == 0:
            return 0.0

        return ((likes + comments) / views) * 100

    @staticmethod
    def tiktok_virality_score(metrics: Dict) -> float:
        """Calculate TikTok virality score"""
        views = metrics.get("views", 0)
        shares = metrics.get("shares", 0)
        videos = metrics.get("videos", 0)

        if videos == 0:
            return 0.0

        return (views * shares) / (videos * 100)


class ExtendedValidators:
    @field_validator("followers", "monthly_listeners", "total_streams")
    def validate_positive_numbers(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Value must be non-negative")
        return v

    @field_validator("engagement_rate", "market_share")
    def validate_percentage(cls, v: float) -> float:
        if not 0 <= v <= 100:
            raise ValueError("Value must be between 0 and 100")
        return v

    @model_validator(mode="after")
    def validate_dates(self) -> "ExtendedValidators":
        start_date = self.start_date
        end_date = self.end_date
        if start_date and end_date and start_date > end_date:
            raise ValueError("end_date must be after start_date")
        return self


class ArtistMetrics(BaseModel):
    """Complete artist metrics from Soundcharts"""

    metadata: ArtistMetadata
    current_stats: ArtistCurrentStats
    audience: ArtistAudienceMetrics
    streaming: ArtistStreamingMetrics
    social: ArtistSocialMetrics
    charts: ArtistChartMetrics
    fanbase_metrics: Dict[str, Dict] = Field(
        description="Fanbase growth and engagement metrics",
        example={
            "total_reach": 5000000,
            "engagement_rate": 4.2,
            "growth_rate": 2.5,
        },
    )
    time_series: Dict[str, List[TimeSeriesMetrics]] = Field(
        default_factory=dict,
        description="Time series data for various metrics",
    )

    def calculate_growth_metrics(self) -> Dict[str, float]:
        """Calculate growth metrics across all platforms"""
        growth_metrics = {}
        for platform, data in self.time_series.items():
            if len(data) >= 2:
                current = data[-1].value
                previous = data[0].value
                time_delta = data[-1].timestamp - data[0].timestamp
                growth_metrics[platform] = MetricAggregation.calculate_growth_rate(
                    current,
                    previous,
                    time_delta,
                )
        return growth_metrics

    def get_platform_scores(self) -> Dict[str, float]:
        """Calculate platform-specific engagement scores"""
        return {
            "spotify": PlatformSpecificMetrics.spotify_engagement_score(
                self.current_stats.spotify or {},
            ),
            "youtube": PlatformSpecificMetrics.youtube_engagement_rate(
                self.current_stats.youtube or {},
            ),
            "tiktok": PlatformSpecificMetrics.tiktok_virality_score(
                self.current_stats.tiktok or {},
            ),
        }


class SongMetadata(BaseModel):
    """Song metadata from /song/metadata"""

    id: str
    title: str
    isrc: Optional[str]
    platforms: Dict[Platform, str] = Field(
        description="Platform-specific IDs",
        example={
            "spotify": "5HCyWlXZPP0y6Gqq8TgA20",
            "apple_music": "1234567890",
        },
    )
    release_date: datetime
    duration_ms: int
    artists: List[Dict[str, str]]  # List of artist IDs and names
    album: Dict[str, str]  # Album metadata
    genres: List[str]
    labels: List[str]
    writers: List[str]
    producers: List[str]
    explicit: bool


class SongStreamingMetrics(BaseModel):
    """Streaming performance from /song/streaming-stats"""

    spotify: Optional[Dict[str, Dict]] = Field(
        example={
            "total_streams": {
                "all_time": 15000000,
                "last_28_days": 500000,
                "daily_average": 17857,
            },
            "playlist_presence": {
                "total_playlists": 1200,
                "editorial_playlists": 15,
                "algorithmic_playlists": 85,
                "user_playlists": 1100,
                "total_reach": 5000000,
            },
            "saves": {
                "total": 250000,
                "daily_average": 892,
            },
        },
    )
    apple_music: Optional[Dict[str, Dict]] = Field(
        example={
            "total_plays": {"all_time": 5000000},
            "playlists": {
                "total_count": 500,
                "editorial_count": 10,
            },
        },
    )
    youtube: Optional[Dict[str, Dict]] = Field(
        example={
            "views": {
                "total": 2000000,
                "daily_average": 7142,
            },
            "likes": 50000,
            "comments": 5000,
        },
    )


class SongChartMetrics(BaseModel):
    """Chart performance from /song/chart-entries"""

    entries: Dict[Platform, List[Dict]] = Field(
        example={
            "spotify": [
                {
                    "date": "2024-03-20",
                    "chart_name": "Top 200",
                    "country": "US",
                    "position": 12,
                    "previous_position": 15,
                    "streams": 500000,
                    "duration_days": 1,
                },
            ],
            "apple_music": [
                {
                    "date": "2024-03-20",
                    "chart_name": "Daily Top 100",
                    "country": "US",
                    "position": 8,
                    "previous_position": 10,
                },
            ],
        },
    )
    peak_positions: Dict[Platform, Dict[str, Dict]] = Field(
        example={
            "spotify": {
                "global": {"peak": 5, "date": "2024-02-15"},
                "US": {"peak": 3, "date": "2024-02-16"},
            },
        },
    )
    chart_history: Dict[str, List[Dict]] = Field(
        description="Historical chart positions over time",
    )


class RadioMetrics(BaseModel):
    """Radio performance from /song/radio-spins"""

    spins: Dict[str, Dict] = Field(
        example={
            "total_spins": 15000,
            "unique_stations": 250,
            "countries": {
                "US": 10000,
                "UK": 3000,
                "DE": 2000,
            },
            "formats": {
                "CHR": 5000,
                "Urban": 4000,
                "AC": 6000,
            },
        },
    )
    audience: Dict[str, int] = Field(
        example={
            "total_reach": 25000000,
            "peak_daily_reach": 1500000,
        },
    )
    trend: Dict[str, Dict] = Field(
        example={
            "weekly_growth": 12.5,
            "monthly_growth": 45.2,
        },
    )


class PlaylistEntry(BaseModel):
    """Playlist entry data from /song/playlist-entries"""

    platform: Platform
    playlist_id: str
    playlist_name: str
    curator_type: str  # editorial, algorithmic, user
    position: int
    added_at: datetime
    followers: int
    monthly_reach: int
    category: Optional[str]
    genres: List[str]


class SongMetrics(BaseModel):
    """Complete song metrics from Soundcharts"""

    metadata: SongMetadata
    streaming: SongStreamingMetrics
    charts: SongChartMetrics
    radio: RadioMetrics
    playlists: List[PlaylistEntry]
    audience_metrics: Dict[str, Dict] = Field(
        example={
            "demographics": {
                "age_groups": {"18-24": 40, "25-34": 35},
                "gender": {"male": 45, "female": 55},
            },
            "geographic": {
                "top_countries": {"US": 40, "UK": 15, "DE": 10},
                "cities": {"New York": 5, "London": 4, "Berlin": 3},
            },
        },
    )


class PlaylistMetadata(BaseModel):
    """Playlist metadata from /playlist/metadata"""

    id: str
    name: str
    platform: Platform
    curator: Dict[str, str] = Field(
        example={
            "id": "spotify",
            "name": "Spotify",
            "type": "editorial",
        },
    )
    followers: int
    description: Optional[str]
    image_url: Optional[str]
    category: Optional[str]
    genres: List[str]


class PlaylistTrackEntry(BaseModel):
    """Track entry in playlist from /playlist/tracklisting-latest"""

    position: int
    added_at: datetime
    song: Dict[str, str]  # Basic song metadata
    artist: Dict[str, str]  # Basic artist metadata
    duration_ms: int
    explicit: bool


class PlaylistMetrics(BaseModel):
    """Complete playlist metrics from Soundcharts"""

    metadata: PlaylistMetadata
    audience: Dict[str, Dict] = Field(
        example={
            "followers": {
                "total": 5000000,
                "daily_change": 1500,
                "weekly_growth_rate": 2.5,
            },
            "reach": {
                "monthly_reach": 15000000,
                "daily_active_users": 750000,
            },
        },
    )
    tracklist: List[PlaylistTrackEntry]
    performance: Dict[str, Dict] = Field(
        example={
            "update_frequency": "daily",
            "average_track_count": 50,
            "turnover_rate": 15.5,  # % of tracks changed per update
            "genre_distribution": {
                "pop": 45,
                "hip-hop": 30,
                "r-n-b": 25,
            },
        },
    )


class SoundchartsAnalytics(BaseModel):
    """Complete analytics structure matching Soundcharts API"""

    timestamp: datetime
    artist_data: Optional[ArtistMetrics]
    song_data: Optional[SongMetrics]
    playlist_data: Optional[PlaylistMetrics]
    platform_stats: Dict[Platform, Dict] = Field(
        description="Platform-specific stats from /referential/platforms endpoints",
        example={
            "spotify": {
                "total_users": 500000000,
                "countries_available": 180,
                "chart_types": ["Top 200", "Viral 50"],
            },
        },
    )


class ChartTypes(str, Enum):
    """Chart types from Soundcharts"""

    SPOTIFY_TOP_200 = "spotify_top_200"
    SPOTIFY_VIRAL_50 = "spotify_viral_50"
    APPLE_MUSIC_DAILY_100 = "apple_music_daily_100"
    APPLE_MUSIC_ALBUMS = "apple_music_albums"
    YOUTUBE_TRENDING = "youtube_trending"
    SHAZAM_TOP_200 = "shazam_top_200"
    DEEZER_TOP_100 = "deezer_top_100"


class RadioFormats(str, Enum):
    """Radio formats from Soundcharts"""

    CHR = "chr"  # Contemporary Hit Radio
    AC = "ac"  # Adult Contemporary
    URBAN = "urban"
    ROCK = "rock"
    COUNTRY = "country"
    LATIN = "latin"
    DANCE = "dance"
    ALTERNATIVE = "alternative"


class AlbumMetadata(BaseModel):
    """Album metadata from /album/metadata"""

    id: str
    title: str
    upc: Optional[str]
    platforms: Dict[Platform, str]
    release_date: datetime
    type: str  # album, single, ep
    artists: List[Dict[str, str]]
    total_tracks: int
    label: str
    genres: List[str]
    image_url: Optional[str]


class AlbumMetrics(BaseModel):
    """Complete album metrics from /album endpoints"""

    metadata: AlbumMetadata
    streaming: Dict[Platform, Dict] = Field(
        example={
            "spotify": {
                "total_streams": 10000000,
                "peak_position": 5,
                "current_position": 15,
                "total_saves": 50000,
            },
            "apple_music": {
                "peak_position": 3,
                "current_position": 12,
                "total_plays": 2000000,
            },
        },
    )
    chart_entries: Dict[Platform, List[Dict]] = Field(
        example={
            "spotify": [
                {
                    "date": "2024-03-20",
                    "chart_name": "Top Albums",
                    "country": "US",
                    "position": 5,
                    "previous_position": 3,
                    "duration_days": 1,
                },
            ],
        },
    )


class RadioStation(BaseModel):
    """Radio station data from /radio/station"""

    id: str
    name: str
    country: str
    format: RadioFormats
    audience_reach: int
    total_daily_plays: int
    top_artists: List[Dict[str, int]]  # artist_id -> play_count
    top_songs: List[Dict[str, int]]  # song_id -> play_count


class RadioAirplay(BaseModel):
    """Radio airplay data from /radio/airplay"""

    song_id: str
    station_id: str
    timestamp: datetime
    duration_ms: int
    audience_reach: int
    market_share: float


class PlaylistCurator(BaseModel):
    """Playlist curator data from /playlist/curator"""

    id: str
    name: str
    platform: Platform
    type: str  # editorial, algorithmic, user
    total_playlists: int
    total_followers: int
    top_genres: Dict[str, float]
    influence_score: float
    playlists: List[str]  # playlist IDs


class PlaylistSnapshot(BaseModel):
    """Playlist snapshot from /playlist/snapshot"""

    playlist_id: str
    timestamp: datetime
    total_tracks: int
    followers: int
    tracks: List[Dict[str, Any]]
    added_tracks: List[str]
    removed_tracks: List[str]
    position_changes: Dict[str, Dict[str, int]]  # track_id -> {old_pos, new_pos}


class MarketMetrics(BaseModel):
    """Market-specific metrics from /market endpoints"""

    country: str
    timestamp: datetime
    streaming: Dict[Platform, Dict] = Field(
        example={
            "spotify": {
                "total_users": 5000000,
                "premium_users": 3000000,
                "market_share": 0.45,
                "revenue": 1200000,
            },
        },
    )
    radio: Dict[str, Dict] = Field(
        example={
            "total_stations": 500,
            "total_audience": 25000000,
            "format_distribution": {
                "CHR": 0.3,
                "Urban": 0.25,
                "AC": 0.45,
            },
        },
    )
    demographics: Dict[str, Dict] = Field(
        example={
            "age_groups": {
                "18-24": 0.25,
                "25-34": 0.35,
                "35-44": 0.20,
                "45+": 0.20,
            },
            "gender": {"male": 0.48, "female": 0.52},
            "income_levels": {
                "low": 0.2,
                "medium": 0.5,
                "high": 0.3,
            },
        },
    )


class CompetitorAnalysis(BaseModel):
    """Competitor analysis from various endpoints"""

    artist_id: str
    competitors: List[Dict[str, Any]] = Field(
        example=[
            {
                "artist_id": "xyz",
                "overlap_score": 0.85,
                "shared_audience": 500000,
                "common_playlists": 150,
                "market_position": {
                    "genre": "pop",
                    "audience_size": "medium",
                    "growth_rate": "high",
                },
            },
        ],
    )
    audience_overlap: Dict[str, float]
    playlist_overlap: Dict[str, int]
    market_share_comparison: Dict[str, Dict[str, float]]


class TrendAnalysis(BaseModel):
    """Trend analysis from /trends endpoints"""

    timeframe: str  # daily, weekly, monthly
    metrics: Dict[str, List[Dict]] = Field(
        example={
            "streams": [
                {
                    "date": "2024-03-20",
                    "value": 150000,
                    "change_percent": 5.2,
                },
            ],
            "playlist_adds": [
                {
                    "date": "2024-03-20",
                    "value": 50,
                    "change_percent": 2.5,
                },
            ],
        },
    )
    forecasts: Dict[str, Dict] = Field(
        example={
            "streams": {
                "next_week": 1200000,
                "next_month": 5000000,
                "confidence": 0.85,
            },
        },
    )


class ExtendedSoundchartsAnalytics(SoundchartsAnalytics):
    """Extended analytics with additional Soundcharts data"""

    album_data: Optional[AlbumMetrics]
    radio_data: Dict[str, RadioStation]
    market_data: Dict[str, MarketMetrics]
    competitor_analysis: Optional[CompetitorAnalysis]
    trends: Optional[TrendAnalysis]
    playlist_curators: Dict[str, PlaylistCurator]
    playlist_snapshots: Dict[str, List[PlaylistSnapshot]]


class MetricsData(BaseModel):
    metrics: Dict[str, List[Dict]] = Field(
        default_factory=dict,
        json_schema_extra={
            "example": {
                "streams": [
                    {
                        "date": "2024-03-20",
                        "value": 150000,
                        "change_percent": 5.2,
                    },
                ],
                "playlist_adds": [
                    {
                        "date": "2024-03-20",
                        "value": 50,
                        "change_percent": 2.5,
                    },
                ],
            },
        },
    )
