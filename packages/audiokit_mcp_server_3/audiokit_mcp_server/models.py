from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class GenreData(BaseModel):
    root: str
    sub: List[str]


class Artist(BaseModel):
    id: str  # Our own UUIDv4
    name: str
    credit_name: Optional[str] = None
    country_code: Optional[str] = None
    biography: Optional[str] = None
    isni: Optional[str] = None
    ipi: Optional[str] = None
    gender: Optional[str] = None
    type: Optional[str] = None
    birth_date: Optional[datetime] = None
    soundcharts_uuid: Optional[str] = None  # Store SoundCharts UUID
    soundcharts_slug: Optional[str] = None  # Store SoundCharts slug
    soundcharts_app_url: Optional[str] = None  # Store SoundCharts app URL
    soundcharts_image_url: Optional[str] = None  # Store SoundCharts image URL


class ISRC(BaseModel):
    value: str
    country_code: str
    country_name: str


class Track(BaseModel):
    id: str  # Our own UUIDv4
    name: str
    credit_name: Optional[str] = None
    isrc: Optional[ISRC] = None  # Nested ISRC object
    release_date: Optional[datetime] = None
    copyright: Optional[str] = None
    app_url: Optional[str] = None
    image_url: Optional[str] = None
    duration: Optional[int] = None
    explicit: Optional[bool] = None
    genres: Optional[List[Dict[str, List[str]]]] = None
    composers: Optional[List[str]] = None
    producers: Optional[List[str]] = None
    language_code: Optional[str] = None
    soundcharts_uuid: Optional[str] = None  # Flattened SoundCharts data
    soundcharts_slug: Optional[str] = None
    soundcharts_app_url: Optional[str] = None
    soundcharts_image_url: Optional[str] = None
    audio_danceability: Optional[float] = None  # Flattened audio features
    audio_energy: Optional[float] = None
    audio_key: Optional[int] = None
    audio_loudness: Optional[float] = None
    audio_mode: Optional[int] = None
    audio_speechiness: Optional[float] = None
    audio_acousticness: Optional[float] = None
    audio_instrumentalness: Optional[float] = None
    audio_liveness: Optional[float] = None
    audio_valence: Optional[float] = None
    audio_tempo: Optional[float] = None
    audio_time_signature: Optional[int] = None
    lyrics_analysis_themes: Optional[List[str]] = None  # Flattened lyrics analysis
    lyrics_analysis_moods: Optional[List[str]] = None
    lyrics_analysis_cultural_reference_people: Optional[List[str]] = None
    lyrics_analysis_cultural_reference_non_people: Optional[List[str]] = None
    lyrics_analysis_brands: Optional[List[str]] = None
    lyrics_analysis_locations: Optional[List[str]] = None
    lyrics_analysis_narrative_style: Optional[str] = None
    lyrics_analysis_emotional_intensity_score: Optional[int] = None
    lyrics_analysis_complexity_score: Optional[int] = None
    lyrics_analysis_repetitiveness_score: Optional[int] = None
    lyrics_analysis_rhyme_scheme_score: Optional[int] = None
    lyrics_analysis_imagery_score: Optional[int] = None


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
