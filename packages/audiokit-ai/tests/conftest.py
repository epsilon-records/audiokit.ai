"""Test configuration and fixtures for AudioKit Pro."""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

from audiokit.models import ArtistData


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_api_key() -> str:
    """Mock API key for testing."""
    return "test_api_key_123"


@pytest.fixture
async def mock_artist_data() -> ArtistData:
    """Sample artist data for testing."""
    return ArtistData(
        id="test-artist-123",
        stage_name="Test Artist",
        genres=["pop", "electronic"],
        social_links={
            "spotify": "https://open.spotify.com/artist/test123",
            "instagram": "https://instagram.com/testartist",
        },
        monthly_listeners=10000,
        followers=5000,
    )


@pytest.fixture
async def mock_knowledge_base() -> AsyncGenerator:
    """Mock knowledge base for testing."""
    mock = AsyncMock()

    # Mock query responses
    mock.query.return_value = {
        "source_nodes": [
            {
                "content": "Test artist bio content",
                "metadata": {
                    "doc_type": "artist_profile",
                    "source": "database",
                },
            },
            {
                "content": "Test performance history",
                "metadata": {
                    "doc_type": "performances",
                    "source": "events_db",
                },
            },
        ]
    }

    yield mock


@pytest.fixture
async def mock_openrouter_client() -> AsyncGenerator:
    """Mock OpenRouter client for testing."""
    mock = AsyncMock()

    # Mock chat completion responses
    mock.chat_completion.return_value = "Generated test content for testing purposes."

    yield mock


@pytest.fixture
async def mock_processor() -> AsyncGenerator:
    """Mock document processor for testing."""
    mock = AsyncMock()

    # Mock processing methods
    mock.process_artist_data.return_value = None
    mock.process_generated_content.return_value = None

    yield mock


@pytest.fixture
def mock_config() -> MagicMock:
    """Mock configuration for testing."""
    mock = MagicMock()

    # Mock model configurations
    mock.models.epk = "gpt-4"
    mock.models.internal_report = "claude-2"
    mock.models.booking = "gpt-3.5-turbo"

    # Mock API configurations
    mock.api.openrouter.base_url = "https://test.openrouter.ai"
    mock.api.openrouter.api_key = "test_key"
    mock.api.headers.referer = "https://test.audiokit.org"
    mock.api.headers.title = "AudioKit Pro Tests"

    return mock
