"""
<ai_instruction>
SOURCE:
  file: apps/web/src/lib/db/schema.ts
  table: artists
  type: drizzle_schema

TASK:
  - Maintain parity between this Pydantic model and the Drizzle schema
  - Ensure all fields from the artists table are represented
  - Preserve type mappings:
    * drizzle text() -> str
    * drizzle boolean() -> bool
    * drizzle timestamp() -> Optional[str]
    * drizzle json() -> List[Dict] or Dict

CONTEXT:
  This model is used by AI agents to process artist data for:
  - EPK generation
  - Internal reports
  - Booking emails
  - Analytics

VALIDATION:
  - All required fields must be present
  - Optional fields should have appropriate defaults
  - name_slug property must be maintained for file paths
</ai_instruction>
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ArtistData(BaseModel):
    # Required fields
    stage_name: str
    email: str
    phone: str

    # Optional fields with defaults
    apple_music: Optional[str] = None
    artist_photos: List[Dict[str, Any]] = Field(default_factory=list)
    bandcamp: Optional[str] = None
    bandsintown: Optional[str] = None
    biography: Optional[str] = None
    birthdate: Optional[str] = None
    city: Optional[str] = None
    created: Optional[str] = None
    facebook: Optional[str] = None
    id: Optional[str] = None
    instagram: Optional[str] = None
    legal_name: Optional[str] = None
    linkedin: Optional[str] = None
    mixcloud: Optional[str] = None
    slug: Optional[str] = None
    snapchat: Optional[str] = None
    songkick: Optional[str] = None
    soundcloud: Optional[str] = None
    spotify: Optional[str] = None
    tiktok: Optional[str] = None
    twitch: Optional[str] = None
    updated: Optional[str] = None
    website: Optional[str] = None
    x: Optional[str] = None  # Twitter/X
    youtube: Optional[str] = None
    country: Optional[str] = None
    anr: Optional[str] = None
    is_signed: bool = False
    org_id: Optional[str] = None

    @property
    def name_slug(self) -> str:
        return self.stage_name.replace(" ", "-").lower()
