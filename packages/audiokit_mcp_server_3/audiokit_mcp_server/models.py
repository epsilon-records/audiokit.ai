from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class Artist(BaseModel):
    id: str
    name: str
    slug: str
    image_url: Optional[str] = None
    country_code: Optional[str] = None
    biography: Optional[str] = None
    isni: Optional[str] = None
    ipi: Optional[str] = None
    gender: Optional[str] = None
    type: Optional[str] = None
    birth_date: Optional[datetime] = None


class Track(BaseModel):
    id: str
    title: str
    release_date: datetime
    duration: int
    explicit: bool
    language: str
    isrc: str


class Album(BaseModel):
    id: str
    title: str
    release_date: datetime
    upc: str
    label: str
    type: str
    track_count: int


class Genre(BaseModel):
    id: str
    root: str
    sub: List[str]


class Label(BaseModel):
    id: str
    name: str
    type: Optional[str] = None


class AudioFeature(BaseModel):
    id: str
    acousticness: Optional[float] = None
    danceability: Optional[float] = None
    energy: Optional[float] = None
    instrumentalness: Optional[float] = None
    key: Optional[int] = None
    liveness: Optional[float] = None
    loudness: Optional[float] = None
    mode: Optional[int] = None
    speechiness: Optional[float] = None
    tempo: Optional[float] = None
    time_signature: Optional[int] = None
    valence: Optional[float] = None


class Lyrics(BaseModel):
    id: str
    text: str
    language: str
    sentiment: Optional[float] = None
    topics: Optional[List[str]] = None


class Annotation(BaseModel):
    id: str
    text: str
    start: int
    end: int


class Platform(BaseModel):
    id: str  # Use the "code" field from the API
    platform: str  # Use the "name" field from the API


class Popularity(BaseModel):
    id: str
    date: Optional[datetime] = None
    platform: str
    score: Optional[float] = None
    rank: Optional[int] = None


class StreamingData(BaseModel):
    id: str
    date: Optional[datetime] = None
    stream_count: Optional[int] = None
    peak_position: Optional[int] = None
    chart_appearances: Optional[int] = None
    playlist_adds: Optional[int] = None
    radio_spins: Optional[int] = None


class Audience(BaseModel):
    id: str
    date: Optional[datetime] = None
    country: Optional[str] = None
    age_group: Optional[str] = None
    gender_distribution: Optional[Dict[str, float]] = None
    top_cities: Optional[List[str]] = None
    listener_affinity: Optional[float] = None


class Role(BaseModel):
    id: str
    name: str  # e.g., "artist", "producer", "composer"
