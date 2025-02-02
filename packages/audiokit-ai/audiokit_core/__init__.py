"""AudioKit Pro - Professional AI-powered music marketing tools.

This package extends the open-source AudioKit SDK with advanced AI-powered
marketing tools and analytics. A valid subscription is required to use this package.

Example:
    >>> from audiokitpro import Pipeline
    >>> pipeline = Pipeline(api_key="your_key")
    >>> await pipeline.generate_epk("artist_id")
"""

from .core import Pipeline, run_audiokit_ai_pipeline
from .processor import DocumentProcessor
from . import ai, marketing

__version__ = "1.0.0"
__all__ = [
    "Pipeline",
    "run_audiokit_ai_pipeline",  # For backwards compatibility
    "DocumentProcessor",
    "ai",
    "marketing",
]
