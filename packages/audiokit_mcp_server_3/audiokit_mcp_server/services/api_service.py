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

    async def _upsert_neo4j_node(self, label: str, properties: Dict) -> None:
        """
        Upsert a Neo4j node using MERGE.
        If node exists, updates its properties. If not, creates it.
        """
        query = f"""
        MERGE (n:{label} {{id: $id}})
        SET n += $props
        """
        async with self.neo4j_driver.session() as session:
            await session.run(
                query,
                id=properties["id"],
                props=properties,
            )

    async def _upsert_neo4j_relationship(
        self,
        from_id: str,
        to_id: str,
        rel_type: str,
        properties: Optional[Dict] = None,
    ) -> None:
        """
        Upsert a Neo4j relationship using MERGE.
        If relationship exists, updates its properties. If not, creates it.
        """
        query = f"""
        MATCH (a {{id: $from_id}}), (b {{id: $to_id}})
        MERGE (a)-[r:{rel_type}]->(b)
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

    PENDING_FILES = {
        "artists": "PENDING_ARTISTS.txt",
        "tracks": "PENDING_TRACKS.txt",
        "albums": "PENDING_ALBUMS.txt",
        "labels": "PENDING_LABELS.txt",
    }

    def _add_to_pending_list(self, node_type: str, node_id: str) -> None:
        """Add a node ID to the appropriate pending list."""
        if node_type not in self.PENDING_FILES:
            raise ValueError(f"Invalid node type: {node_type}")

        with open(self.PENDING_FILES[node_type], "a") as f:
            f.write(f"{node_id}\n")

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
        """Ingest all SoundCharts data for an artist and build Neo4j graph"""
        # Step 1: Search for artist and get UUID
        search_results = await self.soundcharts_service.search_artist(artist_name)
        if not search_results.get("items"):
            raise ValueError(f"No artist found with name: {artist_name}")

        artist_data = search_results["items"][0]
        artist_id = artist_data["uuid"]

        # Step 2: Get all artist metadata
        artist_metadata = await self.soundcharts_service.get_artist_metadata(artist_id)
        await self._process_artist_metadata(artist_metadata)

        # Step 3: Get and process artist songs
        songs = await self.soundcharts_service.get_artist_songs(artist_id)
        for song in songs.get("items", []):
            song_metadata = await self.soundcharts_service.get_song_metadata(
                song["uuid"]
            )
            await self._process_song_metadata(song_metadata)

        # Step 4: Get and process artist albums
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
        audio_node = {
            "id": f"audio_{song_id}",
            "acousticness": audio_data.get("acousticness"),
            "danceability": audio_data.get("danceability"),
            "energy": audio_data.get("energy"),
            "instrumentalness": audio_data.get("instrumentalness"),
            "key": audio_data.get("key"),
            "liveness": audio_data.get("liveness"),
            "loudness": audio_data.get("loudness"),
            "mode": audio_data.get("mode"),
            "speechiness": audio_data.get("speechiness"),
            "tempo": audio_data.get("tempo"),
            "time_signature": audio_data.get("timeSignature"),
            "valence": audio_data.get("valence"),
        }
        await self._upsert_neo4j_node("AudioFeature", audio_node)
        await self._upsert_neo4j_relationship(
            song_id,
            audio_node["id"],
            "HAS_AUDIO_FEATURES",
        )

    async def _create_artist_node(self, artist_data: Dict) -> None:
        """Create an Artist node from artist data."""
        artist_node = {
            "id": artist_data["uuid"],
            "name": artist_data["name"],
            "slug": artist_data["slug"],
            "image_url": artist_data["imageUrl"],
            "country_code": artist_data["countryCode"],
            "biography": artist_data["biography"],
            "isni": artist_data["isni"],
            "ipi": artist_data["ipi"],
            "gender": artist_data["gender"],
            "type": artist_data["type"],
            "birth_date": artist_data["birthDate"],
        }
        await self._upsert_neo4j_node("Artist", artist_node)

    async def _create_track_node(self, track_data: Dict) -> None:
        """Create a Track node from track data."""
        track_node = {
            "id": track_data["uuid"],
            "title": track_data["name"],
            "release_date": track_data["releaseDate"],
            "duration": track_data["duration"],
            "explicit": track_data["explicit"],
            "language": track_data["languageCode"],
            "isrc": track_data["isrc"]["value"],
        }
        await self._upsert_neo4j_node("Track", track_node)

    async def _process_related_entities(
        self, entity_data: Dict, entity_id: str
    ) -> None:
        """Process related entities for a given entity."""
        # Process artists
        if "artists" in entity_data:
            for artist in entity_data["artists"]:
                self._add_to_pending_list("artists", artist["uuid"])
                await self._upsert_neo4j_relationship(
                    entity_id,
                    artist["uuid"],
                    "HAS_ARTIST",
                )

        # Process genres
        if "genres" in entity_data:
            for genre in entity_data["genres"]:
                genre_node = {
                    "id": f"genre_{genre['root']}",
                    "root": genre["root"],
                    "sub": genre["sub"],
                }
                await self._upsert_neo4j_node("Genre", genre_node)
                await self._upsert_neo4j_relationship(
                    entity_id,
                    genre_node["id"],
                    "HAS_GENRE",
                )

        # Process labels
        if "labels" in entity_data:
            for label in entity_data["labels"]:
                self._add_to_pending_list("labels", label["uuid"])
                await self._upsert_neo4j_relationship(
                    entity_id,
                    label["uuid"],
                    "HAS_LABEL",
                )

        # Process producers
        if "producers" in entity_data:
            for producer in entity_data["producers"]:
                producer_node = {
                    "id": f"producer_{producer}",
                    "name": producer,
                }
                await self._upsert_neo4j_node("Producer", producer_node)
                await self._upsert_neo4j_relationship(
                    entity_id,
                    producer_node["id"],
                    "HAS_PRODUCER",
                )

        # Process composers
        if "composers" in entity_data:
            for composer in entity_data["composers"]:
                composer_node = {
                    "id": f"composer_{composer}",
                    "name": composer,
                }
                await self._upsert_neo4j_node("Composer", composer_node)
                await self._upsert_neo4j_relationship(
                    entity_id,
                    composer_node["id"],
                    "HAS_COMPOSER",
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
