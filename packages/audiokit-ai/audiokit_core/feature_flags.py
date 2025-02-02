"""Feature flags management using PostHog"""

from typing import Dict, Any
from posthog import Posthog
from functools import lru_cache

from .logger import Logger
from config import cfg


@lru_cache()
def get_posthog_client() -> Posthog:
    """Get or create PostHog client instance"""
    return Posthog(
        project_api_key=cfg.posthog.project_api_key,
        host=cfg.posthog.host,
    )


class FeatureFlags:
    """Feature flags management"""

    def __init__(self, user_id: str):
        self.client = get_posthog_client()
        self.user_id = user_id
        self._flags_cache: Dict[str, bool] = {}

    def is_enabled(self, flag_name: str, default: bool = False) -> bool:
        """Check if a feature flag is enabled"""
        try:
            # Check cache first
            if flag_name in self._flags_cache:
                return self._flags_cache[flag_name]

            # Get flag value from PostHog
            enabled = self.client.feature_enabled(
                key=flag_name,
                distinct_id=self.user_id,
                default=default,
            )

            # Cache the result
            self._flags_cache[flag_name] = enabled
            return enabled

        except Exception as e:
            Logger.warning(f"Failed to check feature flag {flag_name}: {str(e)}")
            return default

    def get_all_flags(self) -> Dict[str, bool]:
        """Get all feature flags for the user"""
        try:
            # Get all flags from PostHog
            flags = self.client.get_all_flags(distinct_id=self.user_id)

            # Update cache
            self._flags_cache.update(flags)
            return flags

        except Exception as e:
            Logger.warning(f"Failed to get all feature flags: {str(e)}")
            return {}

    def get_flag_payload(self, flag_name: str, default: Any = None) -> Any:
        """Get feature flag payload (for multivariate flags)"""
        try:
            return self.client.get_feature_flag_payload(
                key=flag_name,
                distinct_id=self.user_id,
                default=default,
            )

        except Exception as e:
            Logger.warning(f"Failed to get feature flag payload {flag_name}: {str(e)}")
            return default


# Feature flag names
class Flags:
    """Feature flag constants"""

    # Core features (always enabled)
    PLATFORM_INTEGRATION = "platform-integration"
    KNOWLEDGE_BASE = "knowledge-base"
    DATA_STORAGE = "data-storage"

    # Advanced features (configurable)
    CONFIDENCE_SCORING = "confidence-scoring"
    HISTORICAL_TRACKING = "historical-tracking"
    ADVANCED_VALIDATION = "advanced-validation"
    DEMOGRAPHICS_ANALYSIS = "demographics-analysis"
    COMPETITOR_ANALYSIS = "competitor-analysis"

    @classmethod
    def get_core_flags(cls) -> Dict[str, bool]:
        """Get core feature flags with default values"""
        return {
            cls.PLATFORM_INTEGRATION: True,
            cls.KNOWLEDGE_BASE: True,
            cls.DATA_STORAGE: True,
        }

    @classmethod
    def get_advanced_flags(cls) -> Dict[str, bool]:
        """Get advanced feature flags with default values"""
        return {
            cls.CONFIDENCE_SCORING: False,
            cls.HISTORICAL_TRACKING: False,
            cls.ADVANCED_VALIDATION: False,
            cls.DEMOGRAPHICS_ANALYSIS: False,
            cls.COMPETITOR_ANALYSIS: False,
        }
