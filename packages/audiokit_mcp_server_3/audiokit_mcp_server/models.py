from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class Artist(BaseModel):
    id: str  # Our own UUIDv4
    name: str
    credit_name: Optional[str] = None
    country_code: Optional[str] = None
    genres: Optional[List[Dict[str, List[str]]]] = None  # Match API response structure
    biography: Optional[str] = None
    isni: Optional[str] = None
    ipi: Optional[str] = None
    gender: Optional[str] = None
    type: Optional[str] = None
    birth_date: Optional[datetime] = None
    soundcharts: Optional[Dict] = None  # Namespace for SoundCharts-specific data


class Track(BaseModel):
    id: str  # Our own UUIDv4
    name: str
    credit_name: Optional[str] = None
    isrc: Optional[Dict] = None
    release_date: Optional[datetime] = None
    copyright: Optional[str] = None
    app_url: Optional[str] = None
    image_url: Optional[str] = None
    duration: Optional[int] = None
    explicit: Optional[bool] = None
    genres: Optional[List[Dict[str, List[str]]]] = None
    composers: Optional[List[str]] = None
    producers: Optional[List[str]] = None
    labels: Optional[List[Dict]] = None
    language_code: Optional[str] = None
    soundcharts: Optional[Dict] = None  # Namespace for SoundCharts-specific data
    audio: Optional[Dict] = None  # Audio features stored in a nested object
    lyrics_analysis: Optional[Dict] = None  # Lyrics analysis embedded directly


class Album(BaseModel):
    id: str  # Our own UUIDv4
    name: str
    credit_name: Optional[str] = None
    upc: Optional[str] = None
    release_date: Optional[datetime] = None
    total_tracks: Optional[int] = None
    copyright: Optional[str] = None
    image_url: Optional[str] = None
    labels: Optional[List[Dict]] = None
    type: Optional[str] = None
    soundcharts: Optional[Dict] = None  # Namespace for SoundCharts-specific data


class Genre(BaseModel):
    id: str  # Composite ID: "genre_{root}"
    root: str
    sub: List[str]


class Label(BaseModel):
    id: str  # Our own UUIDv4
    name: str
    type: Optional[str] = None


class Lyrics(BaseModel):
    id: str  # Our own UUIDv4
    text: str
    language: str
    sentiment: Optional[float] = None
    topics: Optional[List[str]] = None


class Annotation(BaseModel):
    id: str  # Composite ID: "annotation_{uuid}"
    text: str
    start: int
    end: int


class Platform(BaseModel):
    id: str  # Use the "code" field from the API
    platform: str  # Use the "name" field from the API


class Popularity(BaseModel):
    id: str  # Composite ID: "popularity_{artist_id}_{platform}_{date}"
    artist_id: str
    platform: str
    date: datetime
    value: Optional[int] = None


class StreamingData(BaseModel):
    id: str  # Composite ID: "streaming_{artist_id}_{platform}_{date}"
    artist_id: str
    platform: str
    date: datetime
    value: Optional[int] = None


class Audience(BaseModel):
    id: str  # Composite ID: "audience_{artist_id}_{platform}_{date}"
    artist_id: str
    platform: str
    date: datetime
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    post_count: Optional[int] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None


class Role(BaseModel):
    id: str  # Composite ID: "role_{name}"
    name: str  # e.g., "artist", "producer", "composer"


class LyricsAnalysis(BaseModel):
    id: str  # Use the track UUID
    themes: List[str]
    moods: List[str]
    cultural_reference_people: List[str]
    cultural_reference_non_people: List[str]
    brands: List[str]
    locations: List[str]
    narrative_style: str
    emotional_intensity_score: int
    complexity_score: int
    repetitiveness_score: int
    rhyme_scheme_score: int
    imagery_score: int
