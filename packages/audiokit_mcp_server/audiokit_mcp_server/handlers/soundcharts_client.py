import os
from typing import Dict, Optional

import aiohttp
from fastapi import HTTPException


class SoundchartsClient:
    """Client for Soundcharts API."""

    def __init__(self):
        """Initialize client with API credentials."""
        self.base_url = "https://customer.api.soundcharts.com/api/v2"
        self.app_id = os.getenv("SOUNDCHARTS_APP_ID")
        self.api_key = os.getenv("SOUNDCHARTS_API_KEY")

    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests.

        Returns:
            Dict[str, str]: Headers with authentication credentials.
        """
        return {
            "x-app-id": self.app_id,
            "x-api-key": self.api_key,
        }

    async def get_artist_by_spotify_uri(self, spotify_uri: str) -> Optional[str]:
        """Get Soundcharts artist ID from Spotify URI"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/artist/by-platform",
                headers=self.get_headers(),
                params={
                    "platform": "spotify",
                    "id": spotify_uri.split(":")[-1],
                },
            ) as response:
                if response.status == 404:
                    return None
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="Soundcharts API error",
                    )
                data = await response.json()
                return data.get("id")

    async def get_artist_data(self, artist_id: str) -> Dict:
        """Get complete artist data from Soundcharts"""
        endpoints = {
            "metadata": f"/artist/{artist_id}/metadata",
            "current_stats": f"/artist/{artist_id}/current-stats",
            "audience": f"/artist/{artist_id}/audience",
            "streaming": f"/artist/{artist_id}/streaming-audience",
            "social": f"/artist/{artist_id}/social",
            "charts": f"/artist/{artist_id}/chart-entries",
        }

        data = {}
        async with aiohttp.ClientSession() as session:
            for key, endpoint in endpoints.items():
                async with session.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.get_headers(),
                ) as response:
                    if response.status != 200:
                        continue
                    data[key] = await response.json()

        return data
