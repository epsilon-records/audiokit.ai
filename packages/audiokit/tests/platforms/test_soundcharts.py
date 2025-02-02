"""Tests for Soundcharts platform processor"""

import pytest
from unittest.mock import patch
from datetime import datetime

from audiokit.platforms.soundcharts import SoundchartsProcessor, SoundchartsResponse
from audiokit.models import ArtistData


@pytest.fixture
def artist_data():
    """Test artist data fixture"""
    return ArtistData(
        id="test_artist",
        name="Test Artist",
        soundcharts_id="test123",
    )


@pytest.fixture
def mock_responses():
    """Mock API response data"""
    return {
        "current_stats": {
            "object": {
                "spotify": {
                    "followers": 1000000,
                    "monthly_listeners": 5000000,
                    "popularity": 75,
                },
                "instagram": {
                    "followers": 500000,
                    "posts": 1200,
                },
                "youtube": {
                    "subscribers": 750000,
                    "views": 25000000,
                },
            },
        },
        "audience": {
            "object": {
                "age_distribution": {
                    "18-24": 0.25,
                    "25-34": 0.45,
                    "35-44": 0.20,
                    "45+": 0.10,
                },
                "gender_distribution": {
                    "male": 0.48,
                    "female": 0.51,
                    "other": 0.01,
                },
                "top_countries": [
                    {"country": "US", "share": 0.35},
                    {"country": "UK", "share": 0.15},
                    {"country": "DE", "share": 0.10},
                ],
            },
        },
        "similar_artists": {
            "items": [
                {
                    "id": "artist1",
                    "name": "Similar Artist 1",
                    "genres": ["electronic", "house"],
                    "spotify_followers": 900000,
                },
                {
                    "id": "artist2",
                    "name": "Similar Artist 2",
                    "genres": ["electronic", "techno"],
                    "spotify_followers": 1200000,
                },
            ],
        },
    }


@pytest.mark.asyncio
async def test_soundcharts_processor_init(artist_data):
    """Test processor initialization"""
    processor = SoundchartsProcessor(artist_data)
    assert processor.base_url == "https://customer.api.soundcharts.com/api/v2"
    assert processor.artist_data == artist_data


@pytest.mark.asyncio
async def test_get_auth_credentials(artist_data):
    """Test authentication headers generation"""
    processor = SoundchartsProcessor(artist_data)
    headers = await processor._get_auth_credentials()
    assert "x-app-id" in headers
    assert "x-api-key" in headers


@pytest.mark.asyncio
async def test_refresh_auth_token(artist_data):
    """Test refresh token raises NotImplementedError"""
    processor = SoundchartsProcessor(artist_data)
    with pytest.raises(NotImplementedError):
        await processor._refresh_auth_token()


@pytest.mark.asyncio
async def test_transform_response(artist_data, mock_responses):
    """Test response transformation"""
    processor = SoundchartsProcessor(artist_data)
    combined_data = {
        "current_stats": mock_responses["current_stats"]["object"],
        "audience": mock_responses["audience"]["object"],
        "similar_artists": mock_responses["similar_artists"]["items"],
    }

    response = processor.transform_response(combined_data)
    assert isinstance(response, SoundchartsResponse)
    assert response.platform == "soundcharts"
    assert response.current_stats == mock_responses["current_stats"]["object"]
    assert response.audience == mock_responses["audience"]["object"]
    assert response.similar_artists == mock_responses["similar_artists"]["items"]


@pytest.mark.asyncio
async def test_fetch_data_success(artist_data, mock_responses):
    """Test successful data fetching"""
    processor = SoundchartsProcessor(artist_data)

    # Mock the _make_request method
    async def mock_make_request(method, url, headers, auth_required):
        if "current-stats" in url:
            return mock_responses["current_stats"]
        elif "audience" in url:
            return mock_responses["audience"]
        elif "similar" in url:
            return mock_responses["similar_artists"]
        raise ValueError(f"Unexpected URL: {url}")

    with patch.object(processor, "_make_request", side_effect=mock_make_request):
        response = await processor.fetch_data()

        assert isinstance(response, SoundchartsResponse)
        assert response.current_stats == mock_responses["current_stats"]["object"]
        assert response.audience == mock_responses["audience"]["object"]
        assert response.similar_artists == mock_responses["similar_artists"]["items"]


@pytest.mark.asyncio
async def test_fetch_data_error(artist_data):
    """Test error handling in data fetching"""
    processor = SoundchartsProcessor(artist_data)

    # Mock the _make_request method to raise an exception
    async def mock_make_request(*args, **kwargs):
        raise Exception("API Error")

    with patch.object(processor, "_make_request", side_effect=mock_make_request):
        with pytest.raises(Exception) as exc_info:
            await processor.fetch_data()
        assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
async def test_fetch_data_partial_response(artist_data, mock_responses):
    """Test handling of partial API responses"""
    processor = SoundchartsProcessor(artist_data)

    # Mock the _make_request method to return partial data
    async def mock_make_request(method, url, headers, auth_required):
        if "current-stats" in url:
            return {"object": {}}  # Empty stats
        elif "audience" in url:
            return mock_responses["audience"]  # Normal audience data
        elif "similar" in url:
            return {"items": []}  # Empty similar artists
        raise ValueError(f"Unexpected URL: {url}")

    with patch.object(processor, "_make_request", side_effect=mock_make_request):
        response = await processor.fetch_data()

        assert isinstance(response, SoundchartsResponse)
        assert response.current_stats == {}
        assert response.audience == mock_responses["audience"]["object"]
        assert response.similar_artists == []


@pytest.mark.asyncio
async def test_rate_limiting(artist_data, mock_responses):
    """Test rate limiting behavior"""
    processor = SoundchartsProcessor(artist_data)

    # Mock the rate limiter
    calls = []
    original_acquire = processor.rate_limiter.acquire

    async def mock_acquire():
        calls.append(datetime.now())
        await original_acquire()

    processor.rate_limiter.acquire = mock_acquire

    # Mock successful API responses
    async def mock_make_request(*args, **kwargs):
        return {"object": {}}

    with patch.object(processor, "_make_request", side_effect=mock_make_request):
        await processor.fetch_data()

        # Should have made 3 API calls (stats, audience, similar)
        assert len(calls) == 3

        # Check time between calls
        if len(calls) > 1:
            for i in range(1, len(calls)):
                time_diff = (calls[i] - calls[i - 1]).total_seconds()
                assert time_diff >= (60 / processor.rate_limiter.requests_per_minute)
