import pytest
from audiokit_mcp_server.main import app
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_soundcharts_analysis():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/analyze/spotify",
            json={
                "spotify_uri": "spotify:artist:3TVXtAsR1Inumwj472S9r4",
                "query": "What are Drake's top performing songs?",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert len(data["analysis"]) > 0


@pytest.mark.asyncio
async def test_soundcharts_error_handling():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test invalid Spotify URI
        response = await client.post(
            "/analyze/spotify",
            json={
                "spotify_uri": "invalid:uri",
                "query": "This should fail",
            },
        )
        assert response.status_code == 400

        # Test missing query
        response = await client.post(
            "/analyze/spotify",
            json={
                "spotify_uri": "spotify:artist:3TVXtAsR1Inumwj472S9r4",
            },
        )
        assert response.status_code == 422
