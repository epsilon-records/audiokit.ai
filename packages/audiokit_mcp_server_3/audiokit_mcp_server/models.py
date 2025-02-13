from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class GenreData(BaseModel):
    root: str
    sub: List[str]


class Artist(BaseModel):
    id: Optional[str] = None  # Our own UUIDv4
    name: str
    credit_name: Optional[str] = None
    country_code: Optional[str] = None
    biography: Optional[str] = None
    isni: Optional[str] = None
    ipi: Optional[str] = None
    gender: Optional[str] = None
    type: Optional[str] = None
    birth_date: Optional[datetime] = None


class ISRC(BaseModel):
    id: Optional[str] = None  # Composite ID: "isrc_{value}"
    value: str
    country_code: str
    country_name: str


class Track(BaseModel):
    id: Optional[str] = None  # Our own UUIDv4
    name: str
    credit_name: Optional[str] = None
    release_date: Optional[datetime] = None
    copyright: Optional[str] = None
    app_url: Optional[str] = None
    image_url: Optional[str] = None
    duration: Optional[int] = None
    explicit: Optional[bool] = None
    composers: Optional[List[str]] = None
    producers: Optional[List[str]] = None
    language_code: Optional[str] = None


class Album(BaseModel):
    id: Optional[str] = None  # Our own UUIDv4
    name: str
    credit_name: Optional[str] = None
    upc: Optional[str] = None
    release_date: Optional[datetime] = None
    total_tracks: Optional[int] = None
    copyright: Optional[str] = None
    image_url: Optional[str] = None
    labels: Optional[List[Dict]] = None
    type: Optional[str] = None


class Genre(BaseModel):
    id: Optional[str] = None  # Composite ID: "genre_{root}"
    root: str
    sub: List[str]


class Label(BaseModel):
    id: Optional[str] = None  # Our own UUIDv4
    name: str
    type: Optional[str] = None


class Lyrics(BaseModel):
    id: Optional[str] = None  # Our own UUIDv4
    text: str
    language: str
    sentiment: Optional[float] = None
    topics: Optional[List[str]] = None


class Annotation(BaseModel):
    id: Optional[str] = None  # Composite ID: "annotation_{uuid}"
    text: str
    start: int
    end: int


class Platform(BaseModel):
    id: Optional[str] = None  # Use the "code" field from the API
    platform: str  # Use the "name" field from the API


class Popularity(BaseModel):
    id: Optional[str] = None  # Composite ID: "popularity_{artist_id}_{platform}_{date}"
    artist_id: str
    platform: str
    date: datetime
    value: Optional[int] = None


class StreamingData(BaseModel):
    id: Optional[str] = None  # Composite ID: "streaming_{artist_id}_{platform}_{date}"
    artist_id: str
    platform: str
    date: datetime
    value: Optional[int] = None


class Audience(BaseModel):
    id: Optional[str] = None  # Composite ID: "audience_{artist_id}_{platform}_{date}"
    artist_id: str
    platform: str
    date: datetime
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    post_count: Optional[int] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None


class Role(BaseModel):
    id: Optional[str] = None  # Composite ID: "role_{name}"
    name: str  # e.g., "artist", "producer", "composer"


class LyricsAnalysis(BaseModel):
    id: Optional[str] = None  # Composite ID: "lyrics_{track_id}"
    themes: Optional[List[str]] = None
    moods: Optional[List[str]] = None
    cultural_reference_people: Optional[List[str]] = None
    cultural_reference_non_people: Optional[List[str]] = None
    brands: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    narrative_style: Optional[str] = None
    emotional_intensity_score: Optional[int] = None
    complexity_score: Optional[int] = None
    repetitiveness_score: Optional[int] = None
    rhyme_scheme_score: Optional[int] = None
    imagery_score: Optional[int] = None


class SoundCharts(BaseModel):
    id: Optional[str] = None  # Composite ID: "soundcharts_{uuid}"
    uuid: str
    type: str  # Entity type: "artist", "track", "album"
    slug: Optional[str] = None
    app_url: Optional[str] = None
    image_url: Optional[str] = None


class Audio(BaseModel):
    id: Optional[str] = None  # Composite ID: "audio_{track_id}"
    danceability: Optional[float] = None
    energy: Optional[float] = None
    key: Optional[int] = None
    loudness: Optional[float] = None
    mode: Optional[int] = None
    speechiness: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    valence: Optional[float] = None
    tempo: Optional[float] = None
    time_signature: Optional[int] = None
