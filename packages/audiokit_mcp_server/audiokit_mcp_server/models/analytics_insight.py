from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class AnalyticsInsight(BaseModel):
    """Model for analytics insights"""

    insight: str
    report_url: str
    data_snapshot: Dict
    timestamp: datetime
    reference_id: Optional[str] = None  # Vector store reference ID
