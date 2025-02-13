from typing import Dict, Optional

import httpx
from structlog import get_logger


logger = get_logger()


class SoundChartsService:
    def __init__(self, settings):
        """Initialize SoundCharts API Service with required credentials."""
        logger.info(
            "🎛️ Initializing SoundChartsService with base URL",
            base_url=settings.soundcharts_api_base,
        )
        self.settings = settings
        self.base_url = settings.soundcharts_api_base
        self.headers = {
            "x-app-id": settings.soundcharts_app_id,
            "x-api-key": settings.soundcharts_api_key,
        }
        logger.debug(
            "🔑 API credentials configured",
            app_id=settings.soundcharts_app_id,
        )

    # Artist Endpoints
    async def get_artist_by_platform_id(self, platform: str, identifier: str) -> Dict:
        """Get artist by platform ID"""
        url = f"{self.base_url}/api/v2.9/artist/by-platform/{platform}/{identifier}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_artist_ids(self, artist_id: str) -> Dict:
        """Get artist IDs across platforms"""
        url = f"{self.base_url}/api/v2/artist/{artist_id}/identifiers"
        logger.info("🆔 Fetching artist platform IDs", artist_id=artist_id, url=url)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                logger.info(
                    "✔️ Artist platform IDs retrieved",
                    artist_id=artist_id,
                    status_code=response.status_code,
                )
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                "⚠️ Failed to fetch artist platform IDs",
                artist_id=artist_id,
                url=e.request.url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise

    async def get_artist_popularity(self, artist_id: str) -> Dict:
        """Get artist popularity across all platforms"""
        platforms = await self.get_platforms()
        popularity_data = {}

        for platform in platforms.get("items", []):
            platform_code = platform.get("code")
            if not platform_code:
                continue

            url = (
                f"{self.base_url}/api/v2/artist/{artist_id}/popularity/{platform_code}"
            )
            logger.info(
                "📊 Fetching artist popularity",
                artist_id=artist_id,
                platform=platform_code,
                url=url,
            )

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=self.headers)
                    response.raise_for_status()
                    popularity_data[platform_code] = response.json()
                    logger.info(
                        "📈 Artist popularity retrieved",
                        artist_id=artist_id,
                        platform=platform_code,
                        status_code=response.status_code,
                    )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.warning(
                        "⚠️ Platform not found for artist popularity",
                        artist_id=artist_id,
                        platform=platform_code,
                        url=e.request.url,
                    )
                else:
                    logger.error(
                        "📉 Failed to fetch artist popularity",
                        artist_id=artist_id,
                        platform=platform_code,
                        url=e.request.url,
                        status_code=e.response.status_code,
                        error=str(e),
                    )
                # Continue with next platform even if one fails
                continue

        return popularity_data

    # Song Endpoints
    async def get_song_by_isrc(self, isrc: str) -> Dict:
        """Get song by ISRC"""
        url = f"{self.base_url}/api/v2/song/by-isrc/{isrc}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_song_lyrics_analysis(self, song_id: str) -> Dict:
        """Get lyrics analysis for a song"""
        url = f"{self.base_url}/api/v2/song/{song_id}/lyrics-analysis"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # Album Endpoints
    async def get_album_by_upc(self, upc: str) -> Dict:
        """Get album by UPC."""
        url = f"{self.base_url}/api/v2/album/by-upc/{upc}"
        logger.info(
            "💿 Fetching album by UPC",
            upc=upc,
            url=url,
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                # Always set the UPC to the one we queried with
                data["upc"] = upc

                logger.info(
                    "📀 Album retrieved by UPC",
                    upc=upc,
                    status_code=response.status_code,
                )
                return data

        except httpx.HTTPStatusError as e:
            logger.error(
                "❌ Failed to fetch album by UPC",
                upc=upc,
                url=e.request.url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "🚨 Unexpected error fetching album by UPC",
                upc=upc,
                error=str(e),
            )
            raise

    async def get_album_tracklisting(self, album_id: str) -> Dict:
        """Get album tracklisting"""
        url = f"{self.base_url}/api/v2/album/{album_id}/tracks"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # Charts Endpoints
    async def get_song_ranking(self, slug: str, date: Optional[str] = None) -> Dict:
        """Get song ranking for a specific date or latest"""
        url = f"{self.base_url}/api/v2/chart/song/{slug}/ranking"
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
        url = f"{self.base_url}/api/v2/playlist/by-platform/{platform}/{identifier}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # Radio Endpoints
    async def get_radio_spins(self, artist_id: str) -> Dict:
        """Get radio spins for an artist"""
        url = f"{self.base_url}/api/v2/artist/{artist_id}/broadcasts"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # TikTok Endpoints
    async def get_tiktok_music_videos(self, artist_id: str) -> Dict:
        """Get TikTok music videos for an artist"""
        url = f"{self.base_url}/api/v2/artist/{artist_id}/shorts/tiktok/api/videos"
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
        url = f"{self.base_url}/api/v2/artist/{artist_id}/audience/{platform}/report"
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
        url = f"{self.base_url}/api/v2/artist/search/{artist_name}"
        logger.info("🔍 Searching for artist", artist_name=artist_name, url=url)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                logger.info(
                    "🎉 Artist search successful",
                    artist_name=artist_name,
                    status_code=response.status_code,
                )
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                "🚨 Artist search failed",
                artist_name=artist_name,
                url=e.request.url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise

    async def get_artist_metadata(self, artist_id: str) -> Dict:
        """Get artist metadata by ID."""
        url = f"{self.base_url}/api/v2.9/artist/{artist_id}"
        logger.info("📄 Fetching artist metadata", artist_id=artist_id, url=url)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                logger.info(
                    "✅ Artist metadata retrieved",
                    artist_id=artist_id,
                    status_code=response.status_code,
                )
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                "❌ Failed to fetch artist metadata",
                artist_id=artist_id,
                url=e.request.url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise

    async def get_artist_songs(
        self,
        artist_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict:
        """Get artist's songs."""
        url = f"{self.base_url}/api/v2.21/artist/{artist_id}/songs"
        params = {"limit": limit, "offset": offset}
        logger.info(
            "🎵 Fetching artist songs",
            artist_id=artist_id,
            url=url,
            limit=limit,
            offset=offset,
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                # Handle missing ISRC codes
                if "items" in data:
                    for song in data["items"]:
                        if "isrc" not in song:
                            logger.warning(
                                "⚠️ Missing ISRC for song",
                                artist_id=artist_id,
                                song_id=song.get("id"),
                            )
                            song["isrc"] = None  # Set default value

                logger.info(
                    "🎶 Artist songs retrieved",
                    artist_id=artist_id,
                    status_code=response.status_code,
                )
                return data

        except httpx.HTTPStatusError as e:
            logger.error(
                "❌ Failed to fetch artist songs",
                artist_id=artist_id,
                url=e.request.url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "🚨 Unexpected error fetching artist songs",
                artist_id=artist_id,
                error=str(e),
            )
            raise

    async def get_artist_albums(
        self,
        artist_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict:
        """Get artist's albums."""
        url = f"{self.base_url}/api/v2.34/artist/{artist_id}/albums"
        params = {"limit": limit, "offset": offset}
        logger.info(
            "💿 Fetching artist albums",
            artist_id=artist_id,
            url=url,
            limit=limit,
            offset=offset,
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                logger.info(
                    "📀 Artist albums retrieved",
                    artist_id=artist_id,
                    status_code=response.status_code,
                )
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                "💾 Failed to fetch artist albums",
                artist_id=artist_id,
                url=e.request.url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise

    async def get_artist_stats(self, artist_id: str) -> Dict:
        """Get artist's current stats."""
        url = f"{self.base_url}/api/v2/artist/{artist_id}/current/stats"
        logger.info(
            "📊 Fetching artist stats",
            artist_id=artist_id,
            url=url,
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                logger.info(
                    "📈 Artist stats retrieved",
                    artist_id=artist_id,
                    status_code=response.status_code,
                )
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                logger.warning(
                    "🔒 Premium-protected route, skipping artist stats",
                    artist_id=artist_id,
                    url=e.request.url,
                )
                return {}  # Return empty dict for premium-protected routes
            logger.error(
                "📉 Failed to fetch artist stats",
                artist_id=artist_id,
                url=e.request.url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise

    async def get_artist_audience(self, artist_id: str) -> Dict:
        """Get artist's audience data across all platforms."""
        platforms = await self.get_platforms()
        audience_data = {}

        for platform in platforms.get("items", []):
            platform_code = platform.get("code")
            if not platform_code:
                continue

            url = f"{self.base_url}/api/v2/artist/{artist_id}/audience/{platform_code}"
            logger.info(
                "👥 Fetching artist audience",
                artist_id=artist_id,
                platform=platform_code,
                url=url,
            )

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=self.headers)
                    response.raise_for_status()
                    audience_data[platform_code] = response.json()
                    logger.info(
                        "✅ Artist audience retrieved",
                        artist_id=artist_id,
                        platform=platform_code,
                        status_code=response.status_code,
                    )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.warning(
                        "⚠️ Platform not found for artist audience",
                        artist_id=artist_id,
                        platform=platform_code,
                        url=e.request.url,
                    )
                else:
                    logger.error(
                        "❌ Failed to fetch artist audience",
                        artist_id=artist_id,
                        platform=platform_code,
                        url=e.request.url,
                        status_code=e.response.status_code,
                        error=str(e),
                    )
                # Continue with next platform even if one fails
                continue

        return audience_data

    async def get_similar_artists(self, artist_id: str) -> Dict:
        """Get similar artists."""
        url = f"{self.base_url}/api/v2/artist/{artist_id}/related"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_platforms(self) -> Dict:
        """Get all available platforms from Soundcharts API"""
        url = f"{self.base_url}/api/v2/referential/platforms"
        logger.info("🖥️ Fetching available platforms", url=url)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                logger.info(
                    "✅ Platforms retrieved",
                    status_code=response.status_code,
                )
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                "❌ Failed to fetch platforms",
                url=e.request.url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise
