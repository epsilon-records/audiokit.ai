import asyncio
import fcntl
import os
from typing import Dict, List, Optional

import httpx
from neo4j import AsyncGraphDatabase
from structlog import get_logger

from ..models import (
    Album,
    Artist,
    AudioFeature,
    Genre,
    Label,
    Platform,
    Role,
    Track,
)
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
        # Add unique constraints on startup
        asyncio.run(self._add_unique_constraints())

    async def _add_unique_constraints(self) -> None:
        """Add unique constraints to Neo4j if they don't already exist."""
        constraints = [
            ("Artist", "id"),
            ("Track", "id"),
            ("Album", "id"),
            ("Genre", "id"),
            ("Label", "id"),
            ("AudioFeature", "id"),
            ("Role", "id"),
        ]

        for label, property in constraints:
            query = f"""
            CREATE CONSTRAINT {label.lower()}_{property}_unique IF NOT EXISTS
            FOR (n:{label}) REQUIRE n.{property} IS UNIQUE
            """
            try:
                async with self.neo4j_driver.session() as session:
                    await session.run(query)
                logger.info(
                    "✅ Added unique constraint",
                    label=label,
                    property=property,
                )
            except Exception as e:
                logger.error(
                    "❌ Failed to add unique constraint",
                    label=label,
                    property=property,
                    error=str(e),
                )
                raise

    async def _upsert_neo4j_node(self, label: str, properties: Dict) -> None:
        """Upsert a Neo4j node with error handling."""
        # Validate properties based on label
        if label == "Artist":
            Artist(**properties)
        elif label == "Track":
            Track(**properties)
        elif label == "Album":
            Album(**properties)
        elif label == "Genre":
            Genre(**properties)
        elif label == "Label":
            Label(**properties)
        elif label == "AudioFeature":
            AudioFeature(**properties)
        elif label == "Role":
            Role(**properties)
        elif label == "Platform":
            Platform(**properties)
        else:
            raise ValueError(f"Invalid label: {label}")

        query = f"""
        MERGE (n:{label} {{id: $id}})
        SET n += $props
        """
        try:
            async with self.neo4j_driver.session() as session:
                await session.run(query, id=properties["id"], props=properties)
        except Exception as e:
            logger.error(
                "❌ Failed to upsert Neo4j node",
                label=label,
                properties=properties,
                error=str(e),
            )
            raise

    async def _upsert_neo4j_relationship(
        self,
        from_id: str,
        to_id: str,
        rel_type: str,
        properties: Optional[Dict] = None,
    ) -> None:
        """Upsert a Neo4j relationship with error handling."""
        query = f"""
        MATCH (a {{id: $from_id}}), (b {{id: $to_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        """
        if properties:
            query += " SET r += $props"
        try:
            async with self.neo4j_driver.session() as session:
                await session.run(
                    query,
                    from_id=from_id,
                    to_id=to_id,
                    props=properties or {},
                )
        except Exception as e:
            logger.error(
                "❌ Failed to upsert Neo4j relationship",
                from_id=from_id,
                to_id=to_id,
                rel_type=rel_type,
                error=str(e),
            )
            raise

    PENDING_FILES = {
        "artists": "PENDING_ARTISTS.txt",
        "tracks": "PENDING_TRACKS.txt",
        "albums": "PENDING_ALBUMS.txt",
        "labels": "PENDING_LABELS.txt",
    }

    def _add_to_pending_list(self, node_type: str, node_id: str) -> None:
        """Add a node ID to the appropriate pending list if it doesn't already exist."""
        if node_type not in self.PENDING_FILES:
            raise ValueError(f"Invalid node type: {node_type}")

        # For producers and composers, use the artists list
        if node_type in ["producers", "composers"]:
            node_type = "artists"

        file_path = self.PENDING_FILES[node_type]

        # Create the file if it doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                pass

        # Use file locking to prevent concurrent writes
        with open(file_path, "r+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)  # Acquire an exclusive lock
            existing_ids = set(line.strip() for line in f.readlines())

            if node_id not in existing_ids:
                f.write(f"{node_id}\n")
            fcntl.flock(f, fcntl.LOCK_UN)  # Release the lock

    async def _process_song_metadata(self, song_metadata: Dict) -> None:
        """Process song metadata and create nodes/relationships."""
        song_object = song_metadata["object"]
        song_id = song_object["uuid"]

        # Create Track node
        await self._create_track_node(song_object)

        # Process audio features
        if "audio" in song_object:
            await self._create_audio_node(song_id, song_object["audio"])

        # Process artists, genres, labels, producers, composers, and featured artists
        await self._process_related_entities(song_object, song_id)

    async def _process_album_metadata(self, album_metadata: Dict) -> None:
        """Process album metadata and create nodes/relationships."""
        album_object = album_metadata["object"]
        album_id = album_object["uuid"]

        # Create Album node
        album_node = {
            "id": album_id,
            "title": album_object["name"],
            "release_date": album_object["release_date"],
            "upc": album_object["upc"],
            "label": album_object["label"],
            "type": album_object["type"],
            "track_count": album_object["track_count"],
        }
        await self._upsert_neo4j_node("Album", album_node)

        # Process related entities
        await self._process_related_entities(album_object, album_id)

        # Process tracklisting
        tracklisting = await self.soundcharts_service.get_album_tracklisting(album_id)
        for track in tracklisting["tracks"]:
            self._add_to_pending_list("tracks", track["uuid"])
            await self._upsert_neo4j_relationship(
                album_id,
                track["uuid"],
                "CONTAINS",
            )

    async def _process_artist_metadata(self, artist_metadata: Dict) -> None:
        """Process artist metadata and create nodes/relationships."""
        artist_object = artist_metadata["object"]
        artist_id = artist_object["uuid"]

        # Create Artist node
        await self._create_artist_node(artist_object)

        # Process genres, platform IDs, popularity data, stats, audience data, and similar artists
        await self._process_related_entities(artist_object, artist_id)

    async def _process_lyrics_metadata(self, lyrics_metadata: Dict) -> None:
        """Process lyrics metadata and create nodes/relationships."""
        lyrics_id = lyrics_metadata["uuid"]

        # Create Lyrics node
        lyrics_node = {
            "id": lyrics_id,
            "text": lyrics_metadata["text"],
            "language": lyrics_metadata["language"],
            "sentiment": lyrics_metadata["sentiment"],
            "topics": lyrics_metadata["topics"],
        }
        await self._upsert_neo4j_node("Lyrics", lyrics_node)

        # Process annotations
        for annotation in lyrics_metadata.get("annotations", []):
            annotation_node = {
                "id": f"annotation_{annotation['uuid']}",
                "text": annotation["text"],
                "start": annotation["start"],
                "end": annotation["end"],
            }
            await self._upsert_neo4j_node("Annotation", annotation_node)
            await self._upsert_neo4j_relationship(
                lyrics_id,
                annotation_node["id"],
                "HAS_ANNOTATION",
            )

    async def ingest_soundcharts_api(self, artist_name: str) -> Dict:
        """Ingest all SoundCharts data for an artist and build Neo4j graph."""
        # Step 1: Search for artist and get UUID
        search_results = await self.soundcharts_service.search_artist(artist_name)
        if not search_results.get("items"):
            raise ValueError(f"No artist found with name: {artist_name}")

        artist_data = search_results["items"][0]
        artist_id = artist_data["uuid"]

        # Step 2: Get all artist metadata
        artist_metadata = await self.soundcharts_service.get_artist_metadata(artist_id)
        await self._process_artist_metadata(artist_metadata)

        # Step 3: Get and process platforms
        platforms = await self.soundcharts_service.get_platforms()
        await self._process_platforms(platforms)

        # Step 4: Get and process artist songs
        songs = await self.soundcharts_service.get_artist_songs(artist_id)
        for song in songs.get("items", []):
            song_metadata = await self.soundcharts_service.get_song_metadata(
                song["uuid"],
            )
            await self._process_song_metadata(song_metadata)

        # Step 5: Get and process artist albums
        albums = await self.soundcharts_service.get_artist_albums(artist_id)
        for album in albums.get("items", []):
            album_metadata = await self.soundcharts_service.get_album_by_upc(
                album["object"]["upc"],
            )
            await self._process_album_metadata(album_metadata)

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

    async def _create_audio_node(self, song_id: str, audio_data: Dict) -> None:
        """Create an AudioFeature node from audio data."""
        audio = AudioFeature(id=f"audio_{song_id}", **audio_data)
        await self._upsert_neo4j_node("AudioFeature", audio.dict())
        await self._upsert_neo4j_relationship(
            song_id,
            audio.id,
            "HAS_AUDIO_FEATURES",
        )

    async def _create_artist_node(self, artist_data: Dict) -> None:
        """Create an Artist node from artist data."""
        artist = Artist(**artist_data)
        await self._upsert_neo4j_node("Artist", artist.dict())

    async def _create_track_node(self, track_data: Dict) -> None:
        """Create a Track node from track data."""
        track = Track(**track_data)
        await self._upsert_neo4j_node("Track", track.dict())

    async def _process_related_entities(
        self,
        entity_data: Dict,
        entity_id: str,
    ) -> None:
        """Process related entities for a given entity."""
        # Process artists
        if "artists" in entity_data:
            for artist in entity_data["artists"]:
                artist_model = Artist(**artist)
                self._add_to_pending_list("artists", artist_model.id)
                await self._upsert_neo4j_node("Artist", artist_model.dict())
                await self._upsert_neo4j_relationship(
                    entity_id,
                    artist_model.id,
                    "HAS_ARTIST",
                )
                # Add artist role
                await self._upsert_neo4j_node(
                    "Role",
                    {"id": "role_artist", "name": "artist"},
                )
                await self._upsert_neo4j_relationship(
                    artist_model.id,
                    "role_artist",
                    "HAS_ROLE",
                )

        # Process genres
        if "genres" in entity_data:
            for genre in entity_data["genres"]:
                genre_model = Genre(id=f"genre_{genre['root']}", **genre)
                await self._upsert_neo4j_node("Genre", genre_model.dict())
                await self._upsert_neo4j_relationship(
                    entity_id,
                    genre_model.id,
                    "HAS_GENRE",
                )

        # Process labels
        if "labels" in entity_data:
            for label in entity_data["labels"]:
                label_model = Label(**label)
                self._add_to_pending_list("labels", label_model.id)
                await self._upsert_neo4j_relationship(
                    entity_id,
                    label_model.id,
                    "HAS_LABEL",
                )

        # Process producers
        if "producers" in entity_data:
            for producer in entity_data["producers"]:
                producer_model = Artist(id=producer, name=producer)
                await self._upsert_neo4j_node("Artist", producer_model.dict())
                await self._upsert_neo4j_relationship(
                    entity_id,
                    producer_model.id,
                    "HAS_PRODUCER",
                )
                # Add producer role
                await self._upsert_neo4j_node(
                    "Role",
                    {"id": "role_producer", "name": "producer"},
                )
                await self._upsert_neo4j_relationship(
                    producer_model.id,
                    "role_producer",
                    "HAS_ROLE",
                )

        # Process composers
        if "composers" in entity_data:
            for composer in entity_data["composers"]:
                composer_model = Artist(id=composer, name=composer)
                await self._upsert_neo4j_node("Artist", composer_model.dict())
                await self._upsert_neo4j_relationship(
                    entity_id,
                    composer_model.id,
                    "HAS_COMPOSER",
                )
                # Add composer role
                await self._upsert_neo4j_node(
                    "Role",
                    {"id": "role_composer", "name": "composer"},
                )
                await self._upsert_neo4j_relationship(
                    composer_model.id,
                    "role_composer",
                    "HAS_ROLE",
                )

        # Process featured artists
        if "featured_artists" in entity_data:
            for artist in entity_data["featured_artists"]:
                self._add_to_pending_list("artists", artist["uuid"])
                await self._upsert_neo4j_relationship(
                    artist["uuid"],
                    entity_id,
                    "FEATURED_ON",
                )

    async def _process_platforms(self, platforms: List[Dict]) -> None:
        """Process platform data and create nodes."""
        logger.info("🖥️ Processing platforms", count=len(platforms))

        for platform in platforms:
            try:
                platform_model = Platform(**platform)
                await self._upsert_neo4j_node("Platform", platform_model.dict())
                logger.debug(
                    "✅ Platform node created",
                    platform_id=platform_model.id,
                    platform_name=platform_model.platform,
                )
            except Exception as e:
                logger.error(
                    "❌ Failed to process platform",
                    platform=platform,
                    error=str(e),
                )
                raise

    async def close(self) -> None:
        """Close all resources."""
        try:
            await self.neo4j_driver.close()
            logger.info("✅ Neo4j driver closed successfully")
        except Exception as e:
            logger.error("❌ Failed to close Neo4j driver", error=str(e))
