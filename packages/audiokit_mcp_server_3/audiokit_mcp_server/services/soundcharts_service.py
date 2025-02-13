from typing import Dict, Optional

import httpx
from structlog import get_logger


logger = get_logger()


class SoundChartsService:
    def __init__(self, settings):
        """Initialize SoundCharts API Service with required credentials."""
        self.settings = settings
        self.base_url = self.settings.soundcharts_api_base
        self.headers = {
            "x-app-id": self.settings.soundcharts_app_id,
            "x-api-key": self.settings.soundcharts_api_key,
        }

    # Artist Endpoints
    async def get_artist_by_platform_id(self, platform: str, identifier: str) -> Dict:
        """Get artist by platform ID"""
        url = f"{self.base_url}/v2.9/artist/by-platform/{platform}/{identifier}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_artist_ids(self, artist_id: str) -> Dict:
        """Get artist IDs across platforms"""
        url = f"{self.base_url}/v2/artist/{artist_id}/identifiers"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_artist_popularity(self, artist_id: str, platform: str) -> Dict:
        """Get artist popularity on specific platform"""
        url = f"{self.base_url}/v2/artist/{artist_id}/popularity/{platform}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # Song Endpoints
    async def get_song_by_isrc(self, isrc: str) -> Dict:
        """Get song by ISRC"""
        url = f"{self.base_url}/v2/song/by-isrc/{isrc}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_song_lyrics_analysis(self, song_id: str) -> Dict:
        """Get lyrics analysis for a song"""
        url = f"{self.base_url}/v2/song/{song_id}/lyrics-analysis"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # Album Endpoints
    async def get_album_by_upc(self, upc: str) -> Dict:
        """Get album by UPC"""
        url = f"{self.base_url}/v2/album/by-upc/{upc}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_album_tracklisting(self, album_id: str) -> Dict:
        """Get album tracklisting"""
        url = f"{self.base_url}/v2/album/{album_id}/tracks"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # Charts Endpoints
    async def get_song_ranking(self, slug: str, date: Optional[str] = None) -> Dict:
        """Get song ranking for a specific date or latest"""
        url = f"{self.base_url}/v2/chart/song/{slug}/ranking"
        if date:
            url += f"/{date}"
        else:
            url += "/latest"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # Playlist Endpoints
    async def get_playlist_by_platform_id(self, platform: str, identifier: str) -> Dict:
        """Get playlist by platform ID"""
        url = f"{self.base_url}/v2/playlist/by-platform/{platform}/{identifier}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # Radio Endpoints
    async def get_radio_spins(self, artist_id: str) -> Dict:
        """Get radio spins for an artist"""
        url = f"{self.base_url}/v2/artist/{artist_id}/broadcasts"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # TikTok Endpoints
    async def get_tiktok_music_videos(self, artist_id: str) -> Dict:
        """Get TikTok music videos for an artist"""
        url = f"{self.base_url}/v2/artist/{artist_id}/shorts/tiktok/videos"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # Audience Endpoints
    async def get_artist_audience_report(
        self,
        artist_id: str,
        platform: str,
        date: Optional[str] = None,
    ) -> Dict:
        """Get audience report for an artist"""
        url = f"{self.base_url}/v2/artist/{artist_id}/audience/{platform}/report"
        if date:
            url += f"/{date}"
        else:
            url += "/latest"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def search_artist(self, artist_name: str) -> Dict:
        """Search artist by name."""
        url = f"{self.base_url}/artist/search"
        params = {"query": artist_name}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_artist_metadata(self, artist_id: str) -> Dict:
        """Get artist metadata by ID."""
        url = f"{self.base_url}/artist/{artist_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_artist_songs(
        self,
        artist_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict:
        """Get artist's songs."""
        url = f"{self.base_url}/artist/{artist_id}/songs"
        params = {"limit": limit, "offset": offset}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_artist_albums(
        self,
        artist_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict:
        """Get artist's albums."""
        url = f"{self.base_url}/artist/{artist_id}/albums"
        params = {"limit": limit, "offset": offset}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_artist_stats(self, artist_id: str) -> Dict:
        """Get artist's current stats."""
        url = f"{self.base_url}/artist/{artist_id}/stats/current"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_artist_audience(self, artist_id: str) -> Dict:
        """Get artist's audience data."""
        url = f"{self.base_url}/artist/{artist_id}/audience"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_similar_artists(self, artist_id: str) -> Dict:
        """Get similar artists."""
        url = f"{self.base_url}/artist/{artist_id}/similar"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
