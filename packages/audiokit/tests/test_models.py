"""Tests for AudioKit SDK data models."""

import pytest
from audiokit.models import ArtistData


async def test_artist_data_creation(mock_artist_data):
    """Test creating an ArtistData instance."""
    artist = ArtistData(**mock_artist_data)
    assert artist.id == mock_artist_data["id"]
    assert artist.stage_name == mock_artist_data["stage_name"]
    assert artist.genres == mock_artist_data["genres"]
    assert artist.social_links == mock_artist_data["social_links"]
    assert artist.monthly_listeners == mock_artist_data["monthly_listeners"]
    assert artist.followers == mock_artist_data["followers"]


async def test_artist_data_validation():
    """Test ArtistData validation."""
    with pytest.raises(ValueError):
        # Should fail without required fields
        ArtistData()

    with pytest.raises(ValueError):
        # Should fail with invalid genre type
        ArtistData(
            id="test-123",
            stage_name="Test",
            genres="pop",  # Should be a list
            social_links={},
            monthly_listeners=0,
            followers=0,
        )


async def test_artist_data_serialization(mock_artist_data):
    """Test ArtistData serialization."""
    artist = ArtistData(**mock_artist_data)
    serialized = artist.model_dump()
    assert isinstance(serialized, dict)
    assert serialized["id"] == mock_artist_data["id"]
    assert serialized["stage_name"] == mock_artist_data["stage_name"]


async def test_artist_data_json(mock_artist_data):
    """Test ArtistData JSON serialization."""
    artist = ArtistData(**mock_artist_data)
    json_str = artist.model_dump_json()
    assert isinstance(json_str, str)

    # Should be able to recreate from JSON
    new_artist = ArtistData.model_validate_json(json_str)
    assert new_artist == artist
