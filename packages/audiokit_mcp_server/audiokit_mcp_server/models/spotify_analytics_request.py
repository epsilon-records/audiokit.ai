from pydantic import BaseModel, Field, field_validator


class SpotifyAnalyticsRequest(BaseModel):
    """Request model for Spotify analytics."""

    spotify_uri: str = Field(
        description="Spotify URI for the artist",
        example="spotify:artist:5K4W6rqBFWDnAN6FQUkS6x",
    )

    @field_validator("spotify_uri")
    def extract_spotify_id(cls, v: str) -> str:
        """Extract artist ID from Spotify URI if full URI is provided"""
        if ":" in v:
            return v.split(":")[-1]
        return v
