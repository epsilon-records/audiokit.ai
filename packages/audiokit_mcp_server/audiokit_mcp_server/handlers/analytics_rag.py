import json
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import aiohttp
import numpy as np
import pandas as pd
import weaviate
from fastapi import HTTPException
from pydantic import BaseModel, Field, root_validator, validator
from scipy import stats

from audiokit_mcp_server.core.config import settings
from audiokit_mcp_server.core.logger import logger
from audiokit_mcp_server.handlers.soundcharts_client import SoundchartsClient


class AnalyticsQuery(BaseModel):
    query: str  # Natural language query about analytics
    data_types: List[str] = ["users", "conversions", "formats"]  # What data to include
    time_range: Optional[str] = "30d"  # Time range to analyze
    context_filter: Optional[Dict[str, str]] = None  # Filter context by metadata
    min_relevance: float = Field(0.7, ge=0, le=1.0)  # Minimum relevance score


class AnalyticsInsight(BaseModel):
    query: str
    insight: str
    data_snapshot: Dict
    timestamp: datetime
    reference_id: Optional[str] = None  # Weaviate reference ID


class WeaviateClient:
    """Weaviate client wrapper"""

    def __init__(self):
        auth_config = (
            weaviate.auth.AuthApiKey(api_key=settings.WEAVIATE_API_KEY)
            if settings.WEAVIATE_API_KEY
            else None
        )

        self.client = weaviate.Client(
            url=settings.WEAVIATE_URL,
            auth_client=auth_config,
        )
        self.init_schema()

    def init_schema(self):
        """Initialize Weaviate schema"""
        schema = {
            "class": "AnalyticsInsight",
            "properties": [
                {"name": "query", "dataType": ["text"]},
                {"name": "insight", "dataType": ["text"]},
                {"name": "dataSnapshot", "dataType": ["text"]},
                {"name": "timestamp", "dataType": ["date"]},
                {"name": "dataTypes", "dataType": ["text[]"]},
                {"name": "timeRange", "dataType": ["text"]},
            ],
        }

        try:
            self.client.schema.create_class(schema)
        except weaviate.exceptions.UnexpectedStatusCodeException:
            pass

    async def store_insight(
        self,
        insight: AnalyticsInsight,
        data_types: List[str],
        time_range: str,
    ) -> str:
        """Store insight in Weaviate"""
        try:
            result = self.client.data_object.create(
                class_name="AnalyticsInsight",
                data_object={
                    "query": insight.query,
                    "insight": insight.insight,
                    "dataSnapshot": str(insight.data_snapshot),
                    "timestamp": insight.timestamp.isoformat(),
                    "dataTypes": data_types,
                    "timeRange": time_range,
                },
            )
            return result["id"]
        except Exception as e:
            logger.error(f"Failed to store insight: {e!s}")
            raise HTTPException(status_code=500, detail="Failed to store insight")

    async def get_related_insights(
        self,
        query: str,
        data_types: List[str],
        min_relevance: float = None,
    ) -> List[Dict]:
        """Get related insights with time weighting"""
        try:
            now = datetime.utcnow()
            min_relevance = min_relevance or settings.MIN_RELEVANCE_SCORE

            result = (
                self.client.query.get(
                    "AnalyticsInsight",
                    ["query", "insight", "timestamp", "dataTypes", "dataSnapshot"],
                )
                .with_near_text({"concepts": [query], "certainty": min_relevance})
                .with_limit(settings.MAX_INSIGHTS)
                .do()
            )

            insights = result["data"]["Get"]["AnalyticsInsight"]
            weighted_insights = []

            for insight in insights:
                age = now - datetime.fromisoformat(insight["timestamp"])

                # Get time weight based on age
                if age <= timedelta(hours=24):
                    time_weight = settings.TIME_WEIGHTS["24h"]
                elif age <= timedelta(days=7):
                    time_weight = settings.TIME_WEIGHTS["7d"]
                elif age <= timedelta(days=30):
                    time_weight = settings.TIME_WEIGHTS["30d"]
                elif age <= timedelta(days=90):
                    time_weight = settings.TIME_WEIGHTS["90d"]
                else:
                    time_weight = settings.TIME_WEIGHTS["older"]

                weighted_insights.append(
                    {
                        **insight,
                        "age_days": age.days,
                        "relevance_score": time_weight,
                    },
                )

            return sorted(
                weighted_insights,
                key=lambda x: x["relevance_score"],
                reverse=True,
            )

        except Exception as e:
            logger.error(f"Failed to get related insights: {e!s}")
            return []


# Initialize clients
weaviate_client = WeaviateClient()
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
    """Store analytics insight in Weaviate"""
    try:
        # Convert data snapshot to string to store in Weaviate
        data_snapshot_str = json.dumps(insight.data_snapshot)

        # Create Weaviate object
        properties = {
            "query": insight.query,
            "insight": insight.insight,
            "dataSnapshot": data_snapshot_str,
            "timestamp": insight.timestamp.isoformat(),
            "dataTypes": data_types,
            "timeRange": time_range,
        }

        # Store in Weaviate
        result = weaviate_client.client.data_object.create(
            data_object=properties,
            class_name="AnalyticsInsight",
        )

        return result["id"]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error storing insight in Weaviate: {e!s}",
        )


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
    query: str,
    data_types: List[str],
    min_relevance: float = ContextConfig.MIN_SIMILARITY,
    limit: int = ContextConfig.MAX_INSIGHTS,
) -> List[Dict]:
    """Get time-weighted related insights from Weaviate"""
    try:
        # Get current time for age calculation
        now = datetime.utcnow()

        # Build Weaviate query with metadata filtering
        result = (
            weaviate_client.client.query.get(
                "AnalyticsInsight",
                [
                    "query",
                    "insight",
                    "timestamp",
                    "dataTypes",
                    "dataSnapshot",
                    "_additional {certainty}",
                ],
            )
            .with_near_text(
                {
                    "concepts": [query],
                    "certainty": min_relevance,
                },
            )
            .with_where(
                {
                    "operator": "Or",
                    "operands": [
                        {
                            "path": ["dataTypes"],
                            "operator": "ContainsAny",
                            "valueStringArray": data_types,
                        },
                    ],
                },
            )
            .with_limit(limit)
            .do()
        )

        insights = result["data"]["Get"]["AnalyticsInsight"]

        # Add time weights and sort by combined relevance
        weighted_insights = []
        for insight in insights:
            # Calculate age and get time weight
            timestamp = datetime.fromisoformat(insight["timestamp"])
            age = now - timestamp

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
            certainty = insight["_additional"]["certainty"]
            combined_score = certainty * time_weight

            # Add metadata for context generation
            weighted_insights.append(
                {
                    **insight,
                    "age_days": age.days,
                    "relevance_score": combined_score,
                    "data_overlap": len(
                        set(insight["dataTypes"]) & set(data_types),
                    )
                    / len(data_types),
                },
            )

        # Sort by combined relevance score
        weighted_insights.sort(key=lambda x: x["relevance_score"], reverse=True)

        return weighted_insights[:limit]

    except Exception as e:
        print(f"Warning: Error fetching related insights: {e!s}")
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


async def call_llm(prompt: str) -> str:
    """Call OpenRouter API with Claude-3-Sonnet"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OpenRouterConfig.API_BASE}/chat/completions",
                headers=OpenRouterConfig.get_headers(),
                json={
                    "model": OpenRouterConfig.MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are an analytics expert for AudioKit, a powerful audio processing toolkit.
                            Analyze data and provide insights about audio processing patterns and user behavior.
                            Focus on actionable insights, clear trends, and specific recommendations.""",
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                },
            ) as response:
                if response.status != 200:
                    error_detail = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"LLM API error: {error_detail}",
                    )

                data = await response.json()
                return data["choices"][0]["message"]["content"]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling LLM: {e!s}",
        )


async def generate_insight(query: str, data: Dict, related_insights: List[Dict]) -> str:
    """Generate natural language insights using LLM with context"""
    # Build context sections
    recent_context = []
    historical_context = []

    for insight in related_insights:
        context_entry = (
            f"Previous insight ({insight['timestamp']}, "
            f"relevance: {insight['relevance_score']:.2f}, "
            f"data overlap: {insight['data_overlap']:.2f}): "
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


async def analyze_data(request: AnalyticsQuery) -> AnalyticsInsight:
    """Generate analytics insights using RAG and store in Weaviate"""
    try:
        # Fetch relevant analytics data
        data = await fetch_analytics_data(
            data_types=request.data_types,
            time_range=request.time_range,
        )

        # Get time-weighted related insights
        related_insights = await get_time_weighted_insights(
            query=request.query,
            data_types=request.data_types,
            min_relevance=request.min_relevance,
        )

        # Generate insight using LLM
        insight = await generate_insight(
            request.query,
            data,
            related_insights,
        )

        # Create insight object
        analytics_insight = AnalyticsInsight(
            query=request.query,
            insight=insight,
            data_snapshot=data,
            timestamp=datetime.utcnow(),
        )

        # Store in Weaviate
        reference_id = await store_insight(
            analytics_insight,
            request.data_types,
            request.time_range,
        )
        analytics_insight.reference_id = reference_id

        return analytics_insight

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing data: {e!s}",
        )


# Initialize Weaviate schema when module loads
weaviate_client.init_schema()


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

    @validator("change_percent")
    def validate_change(cls, v):
        if v is not None:
            return MetricValidation.validate_percentage(v, "change_percent")
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
    """Extended validation rules for metrics"""

    @validator("followers", "monthly_listeners", "total_streams")
    def validate_counts(cls, v, field):
        return MetricValidation.validate_count(
            v,
            field.name,
            MetricValidation.MIN_FOLLOWERS,
            MetricValidation.MAX_FOLLOWERS,
        )

    @validator("engagement_rate", "market_share")
    def validate_rates(cls, v, field):
        return MetricValidation.validate_percentage(v, field.name)

    @root_validator
    def validate_dates(cls, values):
        """Validate date-related fields"""
        if "start_date" in values and "end_date" in values:
            start = values["start_date"]
            end = values["end_date"]
            if start > end:
                raise ValueError("end_date must be after start_date")
        return values


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


class SpotifyAnalyticsRequest(BaseModel):
    """Request for Spotify URI analysis"""

    spotify_uri: str
    query: Optional[str] = "What are the key insights about this artist?"


async def analyze_spotify_uri(request: SpotifyAnalyticsRequest) -> Dict:
    """Analyze artist data from Spotify URI"""
    try:
        # Get Soundcharts artist ID
        artist_id = await soundcharts_client.get_artist_by_spotify_uri(
            request.spotify_uri,
        )
        if not artist_id:
            raise HTTPException(status_code=404, detail="Artist not found")

        # Get artist data
        artist_data = await soundcharts_client.get_artist_data(artist_id)

        # Get related insights
        related_insights = await weaviate_client.get_related_insights(
            query=request.query,
            data_types=["artist"],
        )

        # Generate new insight
        insight = await soundcharts_client.generate_insight(
            query=request.query,
            data=artist_data,
            context=related_insights,
        )

        # Create and store insight
        analytics_insight = AnalyticsInsight(
            query=request.query,
            insight=insight,
            data_snapshot=artist_data,
            timestamp=datetime.utcnow(),
        )

        reference_id = await weaviate_client.store_insight(
            insight=analytics_insight,
            data_types=["artist"],
            time_range="all",
        )

        return {
            "analysis": insight,
            "reference_id": reference_id,
            "timestamp": analytics_insight.timestamp.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze Spotify URI: {e!s}")
        raise HTTPException(status_code=500, detail="Analysis failed")
