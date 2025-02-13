from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, validator


class GenreData(BaseModel):
    root: str
    sub: List[str]


class Artist(BaseModel):
    """Artist model for Soundcharts data."""

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
    soundcharts_uuid: str  # Required SoundCharts UUID
    slug: Optional[str] = None
    app_url: Optional[str] = None
    image_url: Optional[str] = None

    @validator("soundcharts_uuid")
    def validate_soundcharts_uuid(cls, v):
        if not v:
            raise ValueError("SoundCharts UUID cannot be null or empty")
        return v


class ISRC(BaseModel):
    id: Optional[str] = None
    value: str
    country_code: str
    country_name: str

    @validator("id", always=True)
    def generate_composite_id(cls, v, values):
        if not v:
            # Replace spaces with underscores in the ISRC value
            clean_value = values["value"].replace(" ", "_")
            return f"isrc_{clean_value}"
        return v


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
    soundcharts_uuid: str  # SoundCharts UUID for merging


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
    soundcharts_uuid: str  # SoundCharts UUID for merging


class Genre(BaseModel):
    id: Optional[str] = None  # Composite ID: "genre_{root}"
    root: str
    sub: List[str]

    @validator("id", always=True)
    def generate_composite_id(cls, v, values):
        if not v:
            # Replace spaces with underscores in genre root
            clean_root = values["root"].replace(" ", "_")
            return f"genre_{clean_root}"
        return v


class Label(BaseModel):
    id: Optional[str] = None  # Our own UUIDv4
    name: str
    type: Optional[str] = None

    @validator("id", always=True)
    def generate_composite_id(cls, v, values):
        if not v:
            # Replace spaces with underscores in label name
            clean_name = values["name"].replace(" ", "_")
            return f"label_{clean_name}"
        return v


class Lyrics(BaseModel):
    id: Optional[str] = None  # Our own UUIDv4
    text: str
    language: str
    sentiment: Optional[float] = None
    topics: Optional[List[str]] = None

    @validator("id", always=True)
    def generate_composite_id(cls, v, values):
        if not v:
            # Replace spaces with underscores in language
            clean_language = values["language"].replace(" ", "_")
            return f"lyrics_{clean_language}"
        return v


class Annotation(BaseModel):
    id: Optional[str] = None  # Composite ID: "annotation_{uuid}"
    text: str
    start: int
    end: int

    @validator("id", always=True)
    def generate_composite_id(cls, v, values):
        if not v:
            # Replace spaces with underscores in text
            clean_text = values["text"].replace(" ", "_")
            return f"annotation_{clean_text}"
        return v


class Platform(BaseModel):
    id: Optional[str] = None  # Use the "code" field from the API
    platform: str  # Use the "name" field from the API

    @validator("id", always=True)
    def generate_composite_id(cls, v, values):
        if not v:
            # Replace spaces with underscores in platform name
            clean_platform = values["platform"].replace(" ", "_")
            return f"platform_{clean_platform}"
        return v


class Popularity(BaseModel):
    id: Optional[str] = None
    artist_id: str
    platform: str
    date: datetime
    value: Optional[int] = None

    @validator("id", always=True)
    def generate_composite_id(cls, v, values):
        if not v:
            # Replace spaces with underscores in platform name
            clean_platform = values["platform"].replace(" ", "_")
            return f"popularity_{values['artist_id']}_{clean_platform}_{values['date'].isoformat()}"
        return v


class StreamingData(BaseModel):
    id: Optional[str] = None
    artist_id: str
    platform: str
    date: datetime
    value: Optional[int] = None

    @validator("id", always=True)
    def generate_composite_id(cls, v, values):
        if not v:
            # Replace spaces with underscores in platform name
            clean_platform = values["platform"].replace(" ", "_")
            return f"streaming_{values['artist_id']}_{clean_platform}_{values['date'].isoformat()}"
        return v


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

    @validator("id", always=True)
    def generate_composite_id(cls, v, values):
        if not v:
            # Replace spaces with underscores in platform name
            clean_platform = values["platform"].replace(" ", "_")
            return f"audience_{values['artist_id']}_{clean_platform}_{values['date'].isoformat()}"
        return v


class Role(BaseModel):
    id: Optional[str] = None  # Composite ID: "role_{name}"
    name: str  # e.g., "artist", "producer", "composer"

    @validator("id", always=True)
    def generate_composite_id(cls, v, values):
        if not v:
            # Replace spaces with underscores in role name
            clean_name = values["name"].replace(" ", "_")
            return f"role_{clean_name}"
        return v


class LyricsAnalysis(BaseModel):
    id: Optional[str] = None
    track_id: str
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

    @validator("id", always=True)
    def generate_composite_id(cls, v, values):
        if not v:
            return f"lyrics_analysis_{values['track_id']}"
        return v


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

    @validator("id", always=True)
    def generate_composite_id(cls, v, values):
        if not v:
            return f"audio_{values['track_id']}"
        return v
