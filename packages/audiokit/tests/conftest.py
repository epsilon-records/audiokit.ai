"""Test configuration and fixtures for AudioKit SDK."""

import pytest
import asyncio
from typing import AsyncGenerator, Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_artist_data() -> dict:
    """Sample artist data for testing."""
    return {
        "id": "test-artist-123",
        "stage_name": "Test Artist",
        "genres": ["pop", "electronic"],
        "social_links": {
            "spotify": "https://open.spotify.com/artist/test123",
            "instagram": "https://instagram.com/testartist",
        },
        "monthly_listeners": 10000,
        "followers": 5000,
    }


@pytest.fixture
async def mock_platform_client() -> AsyncGenerator:
    """Mock platform client for testing."""
    # Setup (create mock client)
    yield None  # Replace with actual mock client when implementing tests
    # Teardown (cleanup)
