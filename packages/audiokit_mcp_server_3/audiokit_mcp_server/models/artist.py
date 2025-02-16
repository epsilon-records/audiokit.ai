from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Artist(BaseModel):
    id: str
    soundcharts_uuid: str
    name: str
    credit_name: Optional[str] = None
    country_code: Optional[str] = None
    biography: Optional[str] = None
    isni: Optional[str] = None
    ipi: Optional[str] = None
    gender: Optional[str] = None
    type: Optional[str] = None
    birth_date: Optional[datetime] = None
    weight: float = 0.0  # Add weight property with default value 0.0
