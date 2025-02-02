"""Soundcharts data transformer implementation"""

from datetime import datetime
from typing import Dict, Any, List

from .transform import DataTransformer, ArtistMetrics
from .soundcharts import SoundchartsResponse
from ..logger import Logger
from ..feature_flags import Flags


class SoundchartsTransformer(DataTransformer[SoundchartsResponse]):
    """Transform Soundcharts data into standardized format"""

    def transform(self, data: SoundchartsResponse) -> ArtistMetrics:
        """Transform Soundcharts response to standardized metrics"""
        try:
            # Reset metrics for new transformation
            self.metrics = ArtistMetrics()
            timestamp = data.timestamp

            # Process current stats (core feature)
            if data.current_stats:
                self._transform_current_stats(data.current_stats, timestamp)

            # Process audience data (feature flagged)
            if self.flags.is_enabled(Flags.DEMOGRAPHICS_ANALYSIS) and data.audience:
                self._transform_audience(data.audience, timestamp)

            # Add source
            self.metrics.sources.append("soundcharts")

            return self.metrics

        except Exception as e:
            Logger.error(f"Failed to transform Soundcharts data: {str(e)}")
            raise

    def _transform_current_stats(
        self, stats: Dict[str, Dict[str, Any]], timestamp: datetime
    ) -> None:
        """Transform current platform statistics"""
        try:
            for platform, metrics in stats.items():
                # Skip competitor analysis if feature is disabled
                if (
                    not self.flags.is_enabled(Flags.COMPETITOR_ANALYSIS)
                    and platform == "similar_artists"
                ):
                    continue

                for metric_name, value in metrics.items():
                    if isinstance(value, (int, float)):
                        self._add_metric(
                            platform=platform,
                            metric_type=metric_name,
                            value=float(value),
                            timestamp=timestamp,
                            source="soundcharts",
                        )

        except Exception as e:
            Logger.warning(f"Failed to transform current stats: {str(e)}")

    def _transform_audience(
        self, audience: Dict[str, Any], timestamp: datetime
    ) -> None:
        """Transform audience demographics data"""
        if not self.flags.is_enabled(Flags.DEMOGRAPHICS_ANALYSIS):
            return

        try:
            # Extract and standardize age distribution
            age_groups = audience.get("age_distribution", {})

            # Extract and standardize gender distribution
            gender = audience.get("gender_distribution", {})

            # Extract and standardize locations
            locations = []
            for country in audience.get("top_countries", []):
                locations.append(
                    {
                        "country": country.get("country", ""),
                        "share": country.get("share", 0),
                    }
                )

            # Add demographics data
            self._add_demographics(
                age_groups=age_groups,
                gender=gender,
                locations=locations,
                timestamp=timestamp,
                source="soundcharts",
            )

        except Exception as e:
            Logger.warning(f"Failed to transform audience data: {str(e)}")

    def _transform_historical(
        self,
        current: Dict[str, Any],
        historical: List[Dict[str, Any]],
        platform: str,
    ) -> None:
        """Transform historical data into growth metrics"""
        if not self.flags.is_enabled(Flags.HISTORICAL_TRACKING):
            return

        try:
            if not historical:
                return

            # Get most recent historical data point
            previous = historical[0]

            # Extract current and previous metrics
            current_metrics = {}
            previous_metrics = {}

            # Map current metrics
            for metric_name, value in current.items():
                if isinstance(value, (int, float)):
                    current_metrics[self._standardize_metric(metric_name)] = float(
                        value
                    )

            # Map previous metrics
            for metric_name, value in previous.items():
                if isinstance(value, (int, float)):
                    previous_metrics[self._standardize_metric(metric_name)] = float(
                        value
                    )

            # Add growth metrics
            self._add_growth_metrics(platform, current_metrics, previous_metrics)

        except Exception as e:
            Logger.warning(f"Failed to transform historical data: {str(e)}")
