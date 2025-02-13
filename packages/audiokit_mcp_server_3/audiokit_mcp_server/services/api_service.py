from typing import Dict, Optional

import httpx
from neo4j import AsyncGraphDatabase
from structlog import get_logger

from .soundcharts_service import SoundChartsService


logger = get_logger()


class APIService:
    def __init__(self, settings):
        """Initialize API Service with API keys."""
        self.settings = settings
        self.soundcharts_service = SoundChartsService(settings)
        self.neo4j_driver = AsyncGraphDatabase.driver(
            self.settings.neo4j_uri,
            auth=(self.settings.neo4j_user, self.settings.neo4j_password),
        )

    async def _create_neo4j_node(self, label: str, properties: Dict) -> None:
        """Helper method to create a Neo4j node"""
        query = f"CREATE (n:{label} $props)"
        async with self.neo4j_driver.session() as session:
            await session.run(query, props=properties)

    async def _create_neo4j_relationship(
        self,
        from_id: str,
        to_id: str,
        rel_type: str,
        properties: Optional[Dict] = None,
    ) -> None:
        """Helper method to create a Neo4j relationship"""
        query = f"""
        MATCH (a), (b)
        WHERE a.id = $from_id AND b.id = $to_id
        CREATE (a)-[r:{rel_type}]->(b)
        """
        if properties:
            query += " SET r += $props"
        async with self.neo4j_driver.session() as session:
            await session.run(
                query,
                from_id=from_id,
                to_id=to_id,
                props=properties or {},
            )

    async def ingest_soundcharts_api(self, artist_name: str) -> Dict:
        """Ingest all SoundCharts data for an artist and build Neo4j graph"""
        # Step 1: Search for artist and get UUID
        search_results = await self.soundcharts_service.search_artist(artist_name)
        if not search_results.get("items"):
            raise ValueError(f"No artist found with name: {artist_name}")

        artist_data = search_results["items"][0]
        artist_id = artist_data["uuid"]

        # Step 2: Get all artist metadata
        artist_metadata = await self.soundcharts_service.get_artist_metadata(artist_id)
        artist_ids = await self.soundcharts_service.get_artist_ids(artist_id)
        artist_popularity = await self.soundcharts_service.get_artist_popularity(
            artist_id,
        )
        artist_stats = await self.soundcharts_service.get_artist_stats(artist_id)
        artist_audience = await self.soundcharts_service.get_artist_audience(artist_id)

        # Create Artist node with namespaced data
        artist_node = {
            "id": artist_id,
            "name": artist_metadata.get("name"),
            "soundcharts:genre": artist_metadata.get("genre"),
            "soundcharts:country": artist_metadata.get("country"),
            "soundcharts:spotify_id": artist_ids.get("spotify"),
            "soundcharts:lastfm_id": artist_ids.get("lastfm"),
            "soundcharts:chartmetric_id": artist_ids.get("chartmetric"),
            "soundcharts:follower_count": artist_metadata.get("followerCount"),
            "soundcharts:monthly_listeners": artist_metadata.get("monthlyListeners"),
            "soundcharts:biography": artist_metadata.get("biography"),
            "soundcharts:active_since": artist_metadata.get("activeSince"),
            "soundcharts:social_links": artist_metadata.get("socialLinks"),
        }
        await self._create_neo4j_node("Artist", artist_node)

        # Process popularity data with namespacing
        if artist_popularity:
            for platform, data in artist_popularity.items():
                popularity_node = {
                    "id": f"popularity_{artist_id}_{platform}",
                    "platform": platform,
                    "soundcharts:score": data.get("score"),
                    "soundcharts:rank": data.get("rank"),
                    "soundcharts:date": data.get("date"),
                }
                await self._create_neo4j_node("Popularity", popularity_node)
                await self._create_neo4j_relationship(
                    artist_id,
                    popularity_node["id"],
                    "HAS_POPULARITY",
                    {"platform": platform},
                )

        # Process stats with namespacing
        if artist_stats:
            stats_node = {
                "id": f"stats_{artist_id}",
                "soundcharts:stream_count": artist_stats.get("streamCount"),
                "soundcharts:peak_position": artist_stats.get("peakPosition"),
                "soundcharts:chart_appearances": artist_stats.get("chartAppearances"),
                "soundcharts:playlist_adds": artist_stats.get("playlistAdds"),
                "soundcharts:radio_spins": artist_stats.get("radioSpins"),
            }
            await self._create_neo4j_node("StreamingData", stats_node)
            await self._create_neo4j_relationship(
                artist_id,
                stats_node["id"],
                "HAS_STREAMS",
            )

        # Process audience data with namespacing
        if artist_audience:
            audience_node = {
                "id": f"audience_{artist_id}",
                "soundcharts:country": artist_audience.get("country"),
                "soundcharts:age_group": artist_audience.get("ageGroup"),
                "soundcharts:gender_distribution": artist_audience.get(
                    "genderDistribution",
                ),
                "soundcharts:top_cities": artist_audience.get("topCities"),
                "soundcharts:listener_affinity": artist_audience.get(
                    "listenerAffinity",
                ),
            }
            await self._create_neo4j_node("Audience", audience_node)
            await self._create_neo4j_relationship(
                artist_id,
                audience_node["id"],
                "HAS_AUDIENCE",
            )

        # Step 3: Get and process artist songs
        songs = await self.soundcharts_service.get_artist_songs(artist_id)
        for song in songs.get("items", []):
            song_id = song["uuid"]
            song_metadata = await self.soundcharts_service.get_song_by_isrc(
                song["isrc"],
            )

            # Create Track node with namespaced data
            track_node = {
                "id": song_id,
                "title": song_metadata.get("title"),
                "soundcharts:release_date": song_metadata.get("releaseDate"),
                "soundcharts:duration": song_metadata.get("duration"),
                "soundcharts:bpm": song_metadata.get("bpm"),
                "soundcharts:key": song_metadata.get("key"),
                "soundcharts:isrc": song_metadata.get("isrc"),
                "soundcharts:explicit": song_metadata.get("explicit"),
                "soundcharts:language": song_metadata.get("language"),
                "soundcharts:popularity": song_metadata.get("popularity"),
            }
            await self._create_neo4j_node("Track", track_node)
            await self._create_neo4j_relationship(artist_id, song_id, "PERFORMED")

            # Process lyrics with namespacing
            lyrics = await self.soundcharts_service.get_song_lyrics_analysis(song_id)
            if lyrics:
                lyrics_node = {
                    "id": f"lyrics_{song_id}",
                    "soundcharts:text": lyrics.get("text"),
                    "soundcharts:language": lyrics.get("language"),
                    "soundcharts:sentiment": lyrics.get("sentiment"),
                    "soundcharts:topics": lyrics.get("topics"),
                }
                await self._create_neo4j_node("Lyrics", lyrics_node)
                await self._create_neo4j_relationship(
                    song_id,
                    lyrics_node["id"],
                    "HAS_LYRICS",
                )

        # Step 4: Get and process artist albums
        albums = await self.soundcharts_service.get_artist_albums(artist_id)
        for album in albums.get("items", []):
            album_id = album["uuid"]
            album_metadata = await self.soundcharts_service.get_album_by_upc(
                album["upc"],
            )

            # Create Album node with namespaced data
            album_node = {
                "id": album_id,
                "title": album_metadata.get("title"),
                "soundcharts:release_date": album_metadata.get("releaseDate"),
                "soundcharts:upc": album_metadata.get("upc"),
                "soundcharts:label": album_metadata.get("label"),
                "soundcharts:type": album_metadata.get("type"),
                "soundcharts:track_count": album_metadata.get("trackCount"),
                "soundcharts:popularity": album_metadata.get("popularity"),
            }
            await self._create_neo4j_node("Album", album_node)
            await self._create_neo4j_relationship(artist_id, album_id, "PRODUCED_BY")

            # Process tracklisting
            tracklisting = await self.soundcharts_service.get_album_tracklisting(
                album_id,
            )
            for track in tracklisting.get("tracks", []):
                await self._create_neo4j_relationship(
                    album_id,
                    track["uuid"],
                    "CONTAINS",
                )

        # Step 5: Get and process similar artists
        similar_artists = await self.soundcharts_service.get_similar_artists(artist_id)
        for similar in similar_artists.get("items", []):
            similar_id = similar["uuid"]
            await self._create_neo4j_relationship(artist_id, similar_id, "SIMILAR_TO")

        return {"status": "success", "artist_id": artist_id}

    async def query_soundcharts_api(self, artist_name: str) -> Dict:
        """Query SoundCharts API for artist data."""
        return await self.soundcharts_service.search_artist(artist_name)

    async def query_genius_api(self, artist_name: str) -> Dict:
        """Query Genius API for track credits and producer relationships."""
        url = "https://api.genius.com/search"
        params = {"q": artist_name}
        headers = {"Authorization": f"Bearer {self.settings.genius_api_key}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()

    async def query_spotify_api(self, artist_name: str) -> Dict:
        """Query Spotify API for artist discographies and featured artists."""
        url = "https://api.spotify.com/v1/search"
        params = {"q": artist_name, "type": "artist"}
        headers = {"Authorization": f"Bearer {self.settings.spotify_api_key}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()

    async def query_musicbrainz_api(self, artist_name: str) -> Dict:
        """Query MusicBrainz API for songwriting and production credits."""
        url = "https://musicbrainz.org/ws/2/artist"
        params = {"query": artist_name, "fmt": "json"}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def query_billboard_api(self, artist_name: str) -> Dict:
        """Query Billboard API for chart performance history."""
        url = "https://api.billboard.com/charts"
        params = {"artist": artist_name}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def query_lastfm_api(self, artist_name: str) -> Dict:
        """Query Last.fm API for similar artists and tag-based relationships."""
        url = "http://ws.audioscrobbler.com/2.0"
        params = {
            "method": "artist.getinfo",
            "artist": artist_name,
            "api_key": self.settings.lastfm_api_key,
            "format": "json",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
