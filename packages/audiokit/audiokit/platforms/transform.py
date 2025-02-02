"""Data transformation pipeline for platform responses"""

from datetime import datetime
from typing import Dict, Any, List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field, field_validator

from ..logger import Logger
from config import cfg


class MetricValue(BaseModel):
    """Standardized metric value model"""

    value: float
    timestamp: datetime
    source: str
    confidence: float = 1.0  # Confidence score for the metric (0-1)

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Validate confidence score"""
        if not 0 <= v <= 1:
            raise ValueError("Confidence score must be between 0 and 1")
        return v


class Demographics(BaseModel):
    """Standardized demographics model"""

    age_groups: Dict[str, float]
    gender: Dict[str, float]
    locations: List[Dict[str, Any]]
    timestamp: datetime
    source: str

    @field_validator("age_groups", "gender")
    @classmethod
    def validate_distribution(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate distribution sums to 1"""
        if cfg.features.advanced_validation:
            total = sum(v.values())
            if not (0.99 <= total <= 1.01):  # Allow 1% margin of error
                raise ValueError(f"Distribution must sum to 1.0 (got {total})")
        return v


class ArtistMetrics(BaseModel):
    """Standardized artist metrics model"""

    # Core metrics (always included)
    followers: Dict[str, MetricValue] = Field(default_factory=dict)  # By platform
    monthly_listeners: Dict[str, MetricValue] = Field(default_factory=dict)
    popularity_score: Dict[str, MetricValue] = Field(default_factory=dict)

    # Advanced metrics (feature flagged)
    engagement_rate: Dict[str, MetricValue] = Field(default_factory=dict)
    post_frequency: Dict[str, MetricValue] = Field(default_factory=dict)
    stream_count: Dict[str, MetricValue] = Field(default_factory=dict)

    # Audience metrics (feature flagged)
    demographics: Optional[Demographics] = (
        None if cfg.features.demographics_analysis else None
    )

    # Growth metrics (feature flagged)
    follower_growth: Dict[str, float] = Field(default_factory=dict)  # % change
    engagement_growth: Dict[str, float] = Field(default_factory=dict)
    listener_growth: Dict[str, float] = Field(default_factory=dict)

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    sources: List[str] = Field(default_factory=list)


T = TypeVar("T", bound=BaseModel)


class DataTransformer(Generic[T]):
    """Base class for platform-specific data transformers"""

    def __init__(self):
        self.metrics = ArtistMetrics()

    def transform(self, data: T) -> ArtistMetrics:
        """Transform platform-specific data to standardized format"""
        raise NotImplementedError("Transformer must implement transform method")

    def _calculate_growth(
        self, current: float, previous: float, min_value: float = 100
    ) -> float:
        """Calculate growth percentage with minimum value threshold"""
        if not cfg.features.historical_tracking:
            return 0.0

        if previous < min_value:
            return 0.0  # Avoid misleading growth rates for small numbers
        if previous == 0:
            return 0.0
        return ((current - previous) / previous) * 100

    def _calculate_confidence(
        self,
        value: float,
        platform: str,
        metric_type: str,
        timestamp: datetime,
    ) -> float:
        """Calculate confidence score for a metric"""
        if not cfg.features.confidence_scoring:
            return 1.0

        confidence = 1.0

        # Age of data affects confidence
        age_hours = (datetime.now() - timestamp).total_seconds() / 3600
        if age_hours > 24:
            confidence *= max(0.5, 1 - (age_hours - 24) / (7 * 24))  # Decay over a week

        # Very high values might indicate errors
        if value > 1e9:  # Billion+
            confidence *= 0.8

        # Platform-specific adjustments
        platform_weights = {
            "spotify": 1.0,
            "apple_music": 0.9,
            "youtube": 0.95,
            "soundcloud": 0.85,
        }
        confidence *= platform_weights.get(platform, 0.8)

        # Metric-specific adjustments
        metric_weights = {
            "followers": 1.0,
            "monthly_listeners": 0.95,
            "engagement_rate": 0.9,
        }
        confidence *= metric_weights.get(metric_type, 0.85)

        return max(0.1, min(1.0, confidence))  # Ensure between 0.1 and 1.0

    def _standardize_platform(self, platform: str) -> str:
        """Standardize platform names"""
        platform = platform.lower().strip()
        mappings = {
            "spotify": "spotify",
            "applemusic": "apple_music",
            "apple": "apple_music",
            "youtube": "youtube",
            "youtubemusic": "youtube_music",
            "soundcloud": "soundcloud",
            "instagram": "instagram",
            "tiktok": "tiktok",
            "facebook": "facebook",
            "twitter": "twitter",
            "x": "twitter",
        }
        return mappings.get(platform, platform)

    def _standardize_metric(self, metric: str) -> str:
        """Standardize metric names"""
        metric = metric.lower().strip()
        mappings = {
            # Core metrics (always included)
            "followers": "followers",
            "monthly_listeners": "monthly_listeners",
            "monthlylisteners": "monthly_listeners",
            "listener_count": "monthly_listeners",
            "popularity": "popularity_score",
            "pop_score": "popularity_score",
            # Advanced metrics (feature flagged)
            "streams": "stream_count",
            "play_count": "stream_count",
            "playcount": "stream_count",
            "engagement": "engagement_rate",
            "engagement_rate": "engagement_rate",
            "posts": "post_frequency",
            "post_rate": "post_frequency",
        }
        return mappings.get(metric, metric)

    def _add_metric(
        self,
        platform: str,
        metric_type: str,
        value: float,
        timestamp: datetime,
        source: str,
    ) -> None:
        """Add a metric to the standardized format"""
        try:
            # Standardize names
            platform = self._standardize_platform(platform)
            metric_type = self._standardize_metric(metric_type)

            # Calculate confidence
            confidence = self._calculate_confidence(
                value, platform, metric_type, timestamp
            )

            # Create metric value
            metric = MetricValue(
                value=value,
                timestamp=timestamp,
                source=source,
                confidence=confidence,
            )

            # Core metrics (always added)
            if metric_type in ["followers", "monthly_listeners", "popularity_score"]:
                if metric_type == "followers":
                    self.metrics.followers[platform] = metric
                elif metric_type == "monthly_listeners":
                    self.metrics.monthly_listeners[platform] = metric
                elif metric_type == "popularity_score":
                    self.metrics.popularity_score[platform] = metric

            # Advanced metrics (feature flagged)
            elif cfg.features.advanced_validation:
                if metric_type == "engagement_rate":
                    self.metrics.engagement_rate[platform] = metric
                elif metric_type == "post_frequency":
                    self.metrics.post_frequency[platform] = metric
                elif metric_type == "stream_count":
                    self.metrics.stream_count[platform] = metric

        except Exception as e:
            Logger.warning(
                f"Failed to add metric {metric_type} for {platform}: {str(e)}"
            )

    def _add_demographics(
        self,
        age_groups: Dict[str, float],
        gender: Dict[str, float],
        locations: List[Dict[str, Any]],
        timestamp: datetime,
        source: str,
    ) -> None:
        """Add demographics data to the standardized format"""
        if not cfg.features.demographics_analysis:
            return

        try:
            self.metrics.demographics = Demographics(
                age_groups=age_groups,
                gender=gender,
                locations=locations,
                timestamp=timestamp,
                source=source,
            )
        except Exception as e:
            Logger.warning(f"Failed to add demographics data: {str(e)}")

    def _add_growth_metrics(
        self,
        platform: str,
        current_metrics: Dict[str, float],
        previous_metrics: Dict[str, float],
    ) -> None:
        """Add growth metrics to the standardized format"""
        if not cfg.features.historical_tracking:
            return

        try:
            platform = self._standardize_platform(platform)

            # Calculate follower growth
            if "followers" in current_metrics and "followers" in previous_metrics:
                self.metrics.follower_growth[platform] = self._calculate_growth(
                    current_metrics["followers"],
                    previous_metrics["followers"],
                )

            # Calculate engagement growth
            if (
                "engagement_rate" in current_metrics
                and "engagement_rate" in previous_metrics
            ):
                self.metrics.engagement_growth[platform] = self._calculate_growth(
                    current_metrics["engagement_rate"],
                    previous_metrics["engagement_rate"],
                    min_value=0.01,  # 1% minimum for engagement rates
                )

            # Calculate listener growth
            if (
                "monthly_listeners" in current_metrics
                and "monthly_listeners" in previous_metrics
            ):
                self.metrics.listener_growth[platform] = self._calculate_growth(
                    current_metrics["monthly_listeners"],
                    previous_metrics["monthly_listeners"],
                )

        except Exception as e:
            Logger.warning(f"Failed to add growth metrics for {platform}: {str(e)}")
