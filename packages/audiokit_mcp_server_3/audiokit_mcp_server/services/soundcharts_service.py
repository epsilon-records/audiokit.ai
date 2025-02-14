import traceback
from typing import Dict, List, Optional

import httpx
from structlog import get_logger

from ..cache import Cache, cache
from ..models import Artist  # Import from models.py


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
        logger.debug("API headers configured", headers=self.headers)
        self.cache_ttl = settings.redis_cache_ttl
        self.cache = Cache(settings)  # Initialize cache
        self.redis = self.cache.redis  # Expose Redis connection
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
        )  # Initialize HTTP client

    # Artist Endpoints
    @cache()  # Uses self.cache_ttl
    async def get_artist_by_platform_id(self, platform: str, identifier: str) -> Dict:
        """Get artist by platform ID"""
        url = f"{self.base_url}/api/v2.9/artist/by-platform/{platform}/{identifier}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    @cache()  # Uses self.cache_ttl
    async def get_artist_ids(self, artist_id: str) -> Dict:
        """Get artist IDs across platforms"""
        url = f"{self.base_url}/api/v2/artist/{artist_id}/identifiers"
        logger.info("🆔 Fetching artist platform IDs", artist_id=artist_id, url=url)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                logger.info(
                    "✅ Artist platform IDs retrieved",
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

    @cache()  # Uses self.cache_ttl
    async def get_artist_popularity(self, artist_id: str) -> Dict:
        """Get popularity data for an artist."""
        try:
            # Get platforms
            platforms = await self.get_platforms()
            if not isinstance(platforms, list):
                logger.error("Invalid platforms data", platforms=platforms)
                raise ValueError("Platforms data must be a list")

            popularity_data = {}
            for platform in platforms:
                platform_code = platform.get("code")
                if not platform_code:
                    continue

                url = f"{self.base_url}/api/v2/artist/{artist_id}/popularity/{platform_code}"
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=self.headers)
                    response.raise_for_status()
                    platform_data = response.json()
                    popularity_data[platform_code] = platform_data

            return popularity_data
        except Exception as e:
            logger.error(
                "❌ Failed to fetch artist popularity data",
                artist_id=artist_id,
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

    # Song Endpoints
    @cache()  # Uses self.cache_ttl
    async def get_song_by_isrc(self, isrc: str) -> Dict:
        """Get song by ISRC"""
        url = f"{self.base_url}/api/v2/song/by-isrc/{isrc}"
        logger.info(
            "🎵 Fetching song by ISRC",
            isrc=isrc,
            url=url,
        )
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                logger.info(
                    "✅ Song retrieved by ISRC",
                    isrc=isrc,
                    status_code=response.status_code,
                )
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                "❌ Failed to fetch song by ISRC",
                isrc=isrc,
                url=e.request.url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "🚨 Unexpected error fetching song by ISRC",
                isrc=isrc,
                error=str(e),
            )
            raise

    @cache()  # Uses self.cache_ttl
    async def get_song_lyrics_analysis(self, song_id: str) -> Dict:
        """Get lyrics analysis for a song"""
        url = f"{self.base_url}/api/v2/song/{song_id}/lyrics-analysis"
        logger.info(
            "📜 Fetching lyrics analysis",
            song_id=song_id,
            url=url,
        )
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                logger.info(
                    "✅ Lyrics analysis retrieved",
                    song_id=song_id,
                    status_code=response.status_code,
                )
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                "❌ Failed to fetch lyrics analysis",
                song_id=song_id,
                url=e.request.url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "🚨 Unexpected error fetching lyrics analysis",
                song_id=song_id,
                error=str(e),
            )
            raise

    # Album Endpoints
    @cache()  # Uses self.cache_ttl
    async def get_album_metadata(self, album_uuid: str) -> Dict:
        """Get album metadata by UUID from SoundCharts API.

        Args:
            album_uuid: The UUID of the album to retrieve

        Returns:
            Dictionary containing album metadata in the format:
            {
                "type": "album",
                "object": {
                    // album data
                },
                "errors": []
            }
        """
        try:
            # Use API version 2.36 as per documentation
            url = f"{self.base_url}/api/v2.36/album/by-uuid/{album_uuid}"
            logger.info(
                "💿 Fetching album metadata",
                album_uuid=album_uuid,
                url=url,
            )

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                # Validate response structure
                if not isinstance(data, dict) or "object" not in data:
                    logger.error(
                        "❌ Invalid album metadata structure",
                        album_uuid=album_uuid,
                        response=data,
                    )
                    raise ValueError("Invalid album metadata structure")

                logger.info(
                    "✅ Album metadata retrieved",
                    album_uuid=album_uuid,
                    status_code=response.status_code,
                )
                return data

        except httpx.HTTPStatusError as e:
            logger.error(
                "❌ Failed to fetch album metadata",
                album_uuid=album_uuid,
                url=e.request.url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "🚨 Unexpected error fetching album metadata",
                album_uuid=album_uuid,
                error=str(e),
            )
            raise

    @cache()  # Uses self.cache_ttl
    async def get_album_tracklisting(self, album_id: str) -> Dict:
        """Get album tracklisting"""
        url = f"{self.base_url}/api/v2.26/album/{album_id}/tracks"
        logger.info(
            "📋 Fetching album tracklisting",
            album_id=album_id,
            url=url,
        )
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                logger.info(
                    "✅ Album tracklisting retrieved",
                    album_id=album_id,
                    status_code=response.status_code,
                )
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                "❌ Failed to fetch album tracklisting",
                album_id=album_id,
                url=e.request.url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "🚨 Unexpected error fetching album tracklisting",
                album_id=album_id,
                error=str(e),
            )
            raise

    # Charts Endpoints
    @cache()  # Uses self.cache_ttl
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
    @cache()  # Uses self.cache_ttl
    async def get_playlist_by_platform_id(self, platform: str, identifier: str) -> Dict:
        """Get playlist by platform ID"""
        url = f"{self.base_url}/api/v2/playlist/by-platform/{platform}/{identifier}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # Radio Endpoints
    @cache()  # Uses self.cache_ttl
    async def get_radio_spins(self, artist_id: str) -> Dict:
        """Get radio spins for an artist"""
        url = f"{self.base_url}/api/v2/artist/{artist_id}/broadcasts"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # TikTok Endpoints
    @cache()  # Uses self.cache_ttl
    async def get_tiktok_music_videos(self, artist_id: str) -> Dict:
        """Get TikTok music videos for an artist"""
        url = f"{self.base_url}/api/v2/artist/{artist_id}/shorts/tiktok/api/videos"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # Audience Endpoints
    @cache()  # Uses self.cache_ttl
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

    @cache()  # Uses self.cache_ttl
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

    @cache()  # Uses self.cache_ttl
    async def get_artist_metadata(self, artist_id: str) -> Dict:
        """Get artist metadata by ID."""
        url = f"{self.base_url}/api/v2/artist/{artist_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    @cache()  # Uses self.cache_ttl
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

                logger.info(
                    "✅ Artist songs retrieved",
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

    @cache()  # Uses self.cache_ttl
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
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                logger.info(
                    "✅ Artist albums retrieved",
                    artist_id=artist_id,
                    status_code=response.status_code,
                )
                return data
        except httpx.HTTPStatusError as e:
            logger.error(
                "❌ Failed to fetch artist albums",
                artist_id=artist_id,
                url=e.request.url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "🚨 Unexpected error fetching artist albums",
                artist_id=artist_id,
                error=str(e),
            )
            raise

    @cache()  # Uses self.cache_ttl
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
                    "✅ Artist stats retrieved",
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

    @cache()  # Uses self.cache_ttl
    async def get_artist_audience(self, artist_id: str) -> Dict:
        """Get audience data for an artist."""
        try:
            # Get platforms
            platforms = await self.get_platforms()
            if not isinstance(platforms, list):
                logger.error("Invalid platforms data", platforms=platforms)
                raise ValueError("Platforms data must be a list")

            audience_data = {}
            for platform in platforms:
                platform_code = platform.get("code")
                if not platform_code:
                    continue

                url = f"{self.base_url}/api/v2/artist/{artist_id}/audience/{platform_code}"
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=self.headers)
                    response.raise_for_status()
                    platform_data = response.json()
                    audience_data[platform_code] = platform_data

            return audience_data
        except Exception as e:
            logger.error(
                "❌ Failed to fetch artist audience data",
                artist_id=artist_id,
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

    @cache()  # Uses self.cache_ttl
    async def get_similar_artists(self, artist_id: str) -> Dict:
        """Get similar artists."""
        url = f"{self.base_url}/api/v2/artist/{artist_id}/related"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    @cache()  # Uses self.cache_ttl
    async def get_platforms(self) -> List[Dict]:
        """Get all platforms from the SoundCharts API."""
        url = f"{self.base_url}/api/v2/referential/platforms"
        logger.info("🖥️ Fetching available platforms", url=url)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                platforms = [
                    {
                        "id": platform["code"],  # Map "code" to "id"
                        "platform": platform["name"],  # Map "name" to "platform"
                    }
                    for platform in data["items"]
                ]
                logger.info(
                    "✅ Platforms retrieved",
                    count=len(platforms),
                    status_code=response.status_code,
                )
                return platforms
        except httpx.HTTPStatusError as e:
            logger.error(
                "❌ Failed to fetch platforms",
                url=url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "🚨 Unexpected error fetching platforms",
                url=url,
                error=str(e),
            )
            raise

    @cache()  # Uses self.cache_ttl
    async def get_song_metadata(self, song_id: str) -> Dict:
        """
        Get detailed metadata for a song by its ID.

        Args:
            song_id: The UUID of the song.

        Returns:
            Dictionary containing song metadata in the format:
            {
                "type": "song",
                "object": {
                    // song data
                },
                "errors": []
            }
        """
        url = f"{self.base_url}/api/v2.25/song/{song_id}"
        logger.info(
            "🎵 Fetching song metadata",
            song_id=song_id,
            url=url,
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                # Validate response structure
                if not isinstance(data, dict) or "object" not in data:
                    logger.error(
                        "❌ Invalid song metadata structure",
                        song_id=song_id,
                        response=data,
                    )
                    raise ValueError("Invalid song metadata structure")

                logger.info(
                    "✅ Song metadata retrieved",
                    song_id=song_id,
                    status_code=response.status_code,
                )
                return data
        except httpx.HTTPStatusError as e:
            logger.error(
                "❌ Failed to fetch song metadata",
                song_id=song_id,
                url=e.request.url,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "🚨 Unexpected error fetching song metadata",
                song_id=song_id,
                error=str(e),
            )
            raise

    async def create_isrc_node(self, isrc_data: Dict, track_id: str) -> None:
        """Create ISRC node and relationship to track."""
        try:
            # Create ISRC node
            isrc_node = await self.graph.create_node(
                "ISRC",
                code=isrc_data["code"],
                country_code=isrc_data["country_code"],
                country_name=isrc_data["country_name"],
            )

            # Create relationship between track and ISRC
            await self.graph.create_relationship(
                from_node_id=track_id,
                to_node_id=isrc_node.id,
                relationship_type="HAS_ISRC",
            )

            logger.info(
                "✅ Created ISRC node and relationship",
                isrc=isrc_data["code"],
                track_id=track_id,
            )
        except Exception as e:
            logger.error(
                "❌ Failed to create ISRC node",
                isrc=isrc_data["code"],
                track_id=track_id,
                error=str(e),
            )
            raise

    async def process_artist_data(self, artist_data: dict) -> Artist:
        """Process raw artist data from Soundcharts API."""
        try:
            # Log the raw response for debugging
            logger.debug("Raw artist data", data=artist_data)

            # Extract the nested 'object' dictionary
            artist_object = artist_data.get("object", {})

            # Log the artist object for debugging
            logger.debug("Artist object", object=artist_object)

            # Validate that uuid exists and is not null
            if "uuid" not in artist_object:
                logger.error("Missing uuid in artist data", artist_data=artist_data)
                raise ValueError("Artist data is missing required field: uuid")

            if artist_object["uuid"] is None:
                logger.error("Null uuid in artist data", artist_data=artist_data)
                raise ValueError("Artist data contains null uuid")

            # Transform the data to match the Artist model requirements
            transformed_data = {
                "id": artist_object.get("id"),
                "name": artist_object.get("name"),
                "soundcharts_uuid": artist_object[
                    "uuid"
                ],  # Direct access since we validated
                "slug": artist_object.get("slug"),
                "app_url": artist_object.get("appUrl") or "",
                "image_url": artist_object.get("imageUrl") or "",
                "credit_name": artist_object.get("creditName"),
                "country_code": artist_object.get("countryCode"),
                "biography": artist_object.get("biography"),
                "isni": artist_object.get("isni"),
                "ipi": artist_object.get("ipi"),
                "gender": artist_object.get("gender"),
                "type": artist_object.get("type"),
                "birth_date": artist_object.get("birthDate"),
            }

            # Log the transformed data before creating the Artist
            logger.debug("Transformed artist data", data=transformed_data)

            artist = Artist(**transformed_data)

            # Log the final Artist model
            logger.debug("Created Artist model", artist=artist.dict())

            return artist
        except Exception as e:
            logger.error("Failed to process artist data", error=str(e))
            raise

    @cache()  # Uses self.cache_ttl
    async def get_lyrics_analysis(self, track_id: str) -> Dict:
        """Get lyrics analysis for a track."""
        url = f"{self.base_url}/api/v2/song/{track_id}/lyrics-analysis"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    @cache()  # Uses self.cache_ttl
    async def get_artist_streaming_data(self, artist_id: str) -> Dict:
        """Get streaming data for an artist across all platforms."""
        try:
            # Get platforms
            platforms = await self.get_platforms()
            if not isinstance(platforms, list):
                logger.error("Invalid platforms data", platforms=platforms)
                raise ValueError("Platforms data must be a list")

            streaming_data = {}
            for platform in platforms:
                platform_code = platform.get("code")
                if not platform_code:
                    continue

                url = f"{self.base_url}/api/v2/artist/{artist_id}/streaming/{platform_code}"
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url, headers=self.headers)
                        response.raise_for_status()
                        platform_data = response.json()
                        streaming_data[platform_code] = platform_data
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        logger.warning(
                            "⚠️ Streaming data not found for platform",
                            artist_id=artist_id,
                            platform=platform_code,
                        )
                    else:
                        logger.error(
                            "❌ Failed to fetch streaming data for platform",
                            artist_id=artist_id,
                            platform=platform_code,
                            error=str(e),
                        )
                    continue

            return streaming_data
        except Exception as e:
            logger.error(
                "❌ Failed to fetch artist streaming data",
                artist_id=artist_id,
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise
