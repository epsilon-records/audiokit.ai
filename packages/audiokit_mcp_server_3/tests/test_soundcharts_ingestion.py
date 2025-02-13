from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from audiokit_mcp_server.services.api_service import APIService
from neo4j import AsyncGraphDatabase


@pytest.fixture
def mock_settings():
    class MockSettings:
        soundcharts_api_base = "https://api.soundcharts.com"
        soundcharts_app_id = "test-app-id"
        soundcharts_api_key = "test-api-key"
        neo4j_uri = "bolt://localhost:7687"
        neo4j_user = "neo4j"
        neo4j_password = "password"

    return MockSettings()


@pytest.fixture
def api_service(mock_settings):
    service = APIService(mock_settings)
    # Mock the soundcharts_service
    service.soundcharts_service = MagicMock()
    return service


@pytest.mark.asyncio
async def test_ingest_soundcharts_api(api_service):
    # Mock API responses
    mock_artist_data = {
        "items": [
            {
                "uuid": "artist-123",
                "name": "Test Artist",
                "genre": "Pop",
                "country": "US",
            },
        ],
    }

    mock_artist_metadata = {
        "name": "Test Artist",
        "genre": "Pop",
        "country": "US",
        "followerCount": 1000,
        "monthlyListeners": 50000,
        "biography": "Test bio",
        "activeSince": 2010,
        "socialLinks": {"twitter": "test"},
    }

    mock_artist_ids = {
        "spotify": "spotify-123",
        "lastfm": "lastfm-123",
        "chartmetric": "chartmetric-123",
    }

    # Configure mock methods
    api_service.soundcharts_service.search_artist = AsyncMock(
        return_value=mock_artist_data,
    )
    api_service.soundcharts_service.get_artist_metadata = AsyncMock(
        return_value=mock_artist_metadata,
    )
    api_service.soundcharts_service.get_artist_ids = AsyncMock(
        return_value=mock_artist_ids,
    )

    # Create Neo4j mocks
    mock_session = MagicMock()
    mock_session.run = AsyncMock()

    # Create an async context manager for the session
    async def mock_aenter():
        return mock_session

    async def mock_aexit(exc_type, exc, tb):
        pass

    mock_session_context = MagicMock()
    mock_session_context.__aenter__ = mock_aenter
    mock_session_context.__aexit__ = mock_aexit

    # Create the driver mock with proper session method
    mock_driver = MagicMock(spec=AsyncGraphDatabase.driver)
    mock_driver.session = MagicMock(return_value=mock_session_context)

    with patch("neo4j.AsyncGraphDatabase.driver", return_value=mock_driver):
        # Run the ingestion
        result = await api_service.ingest_soundcharts_api("Test Artist")

        # Verify results
        assert result["status"] == "success"
        assert result["artist_id"] == "artist-123"

        # Verify Neo4j node creation
        mock_session.run.assert_any_call(
            "CREATE (n:Artist $props)",
            props={
                "id": "artist-123",
                "soundcharts_name": "Test Artist",
                "soundcharts_genre": "Pop",
                "soundcharts_country": "US",
                "soundcharts_spotify_id": "spotify-123",
                "soundcharts_lastfm_id": "lastfm-123",
                "soundcharts_chartmetric_id": "chartmetric-123",
                "soundcharts_follower_count": 1000,
                "soundcharts_monthly_listeners": 50000,
                "soundcharts_biography": "Test bio",
                "soundcharts_active_since": 2010,
                "soundcharts_social_links": {"twitter": "test"},
            },
        )


@pytest.mark.asyncio
async def test_ingest_soundcharts_api_not_found(api_service):
    api_service.soundcharts_service.search_artist = AsyncMock(
        return_value={"items": []},
    )
    with pytest.raises(ValueError, match="No artist found with name: Unknown Artist"):
        await api_service.ingest_soundcharts_api("Unknown Artist")
