import asyncio
import traceback
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import aioredis
import httpx
from neo4j import AsyncGraphDatabase
from structlog import get_logger

from ..models import (
    Album,
    Artist,
    Genre,
    Label,
    LyricsAnalysis,
    Platform,
    Popularity,
    Track,
    sanitize_id_string,
)
from ..utils.deduplication_queue import DeduplicationQueue
from .soundcharts_service import SoundChartsService


logger = get_logger()


class APIService:
    def __init__(self, settings):
        """Initialize API service with required configurations."""
        self.settings = settings
        self.neo4j_driver = None
        self.redis = None
        self.deduplication_queue = None
        self.soundcharts_service = SoundChartsService(settings)

    async def startup(self):
        """Initialize required resources."""
        # Initialize Redis
        self.redis = await aioredis.from_url(
            self.settings.redis_url,
            decode_responses=True,
        )
        logger.info("✅ Redis connection established")

        # Initialize Neo4j driver
        self.neo4j_driver = AsyncGraphDatabase.driver(
            self.settings.neo4j_uri,
            auth=(self.settings.neo4j_user, self.settings.neo4j_password),
        )
        logger.info("✅ Neo4j driver initialized")

        # Initialize deduplication queue
        self.deduplication_queue = DeduplicationQueue(
            self.settings.redis_url,
            ttl=self.settings.redis_cache_ttl,
            redis_connection=self.redis,
        )
        await self.deduplication_queue.connect()

        # Clear using queue's own method
        await self.deduplication_queue.clear()
        logger.info("🧹 Cleared Redis deduplication queue on startup")

    async def _add_unique_constraints(self) -> None:
        """Add unique constraints to Neo4j."""
        constraints = [
            ("Artist", "id"),
            ("Genre", "id"),
            ("Track", "id"),
            ("Album", "id"),
            ("Label", "name"),
            ("Role", "id"),
            ("Platform", "id"),
            ("Audience", "id"),
            ("Popularity", "id"),
            ("StreamingData", "id"),
            ("LyricsAnalysis", "id"),
            ("ISRC", "value"),
            ("Audio", "id"),
        ]

        for label, property in constraints:
            try:
                query = f"""
                CREATE CONSTRAINT {label.lower()}_{property}_unique IF NOT EXISTS
                FOR (n:{label}) REQUIRE n.{property} IS UNIQUE
                """
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
                    error=str(e),
                )
                raise

    async def _upsert_neo4j_node(self, label: str, properties: Dict) -> None:
        """Upsert a Neo4j node with error handling."""
        try:
            node_id = properties["id"]

            # Check if node has been recently processed
            if await self.deduplication_queue.is_processed(node_id):
                logger.debug(
                    "Node recently processed, skipping",
                    label=label,
                    id=node_id,
                )
                return

            # Proceed with upsert
            merge_key = self._get_merge_key(label)
            query = f"""
            MERGE (n:{label} {{{merge_key}: ${merge_key}}})
            SET n += $props, n.last_updated = $now
            """
            async with self.neo4j_driver.session() as session:
                await asyncio.wait_for(
                    session.run(
                        query,
                        **{merge_key: properties[merge_key]},
                        props=properties,
                        now=datetime.utcnow(),
                    ),
                    timeout=5.0,  # 5-second timeout
                )

            # Mark node as processed
            await self.deduplication_queue.mark_processed(node_id)
        except asyncio.TimeoutError:
            logger.error("Neo4j query timed out", label=label, id=node_id)
        except Exception as e:
            logger.error("❌ Failed to upsert Neo4j node", label=label, error=str(e))
            raise

    async def _upsert_neo4j_relationship(
        self,
        from_id: str,
        to_id: str,
        rel_type: str,
        properties: Optional[Dict] = None,
    ) -> None:
        """Create or update a Neo4j relationship between two nodes."""
        try:
            # First verify both nodes exist
            from_exists = await self._neo4j_node_exists(from_id)
            to_exists = await self._neo4j_node_exists(to_id)

            if not from_exists or not to_exists:
                logger.error(
                    "Nodes not found for relationship",
                    from_id=from_id,
                    from_exists=from_exists,
                    to_id=to_id,
                    to_exists=to_exists,
                )
                raise ValueError("Nodes not found for relationship")

            # Create the relationship
            query = (
                f"MATCH (a), (b) "
                f"WHERE a.id = $from_id AND b.id = $to_id "
                f"MERGE (a)-[r:{rel_type}]->(b) "
                f"SET r += $properties"
            )
            await self.neo4j_driver.execute_query(
                query,
                from_id=from_id,
                to_id=to_id,
                properties=properties or {},
            )
            logger.debug(
                "Created relationship",
                from_id=from_id,
                to_id=to_id,
                rel_type=rel_type,
            )
        except Exception as e:
            logger.error(
                "❌ Failed to upsert Neo4j relationship",
                error=str(e),
                from_id=from_id,
                to_id=to_id,
                rel_type=rel_type,
                stack_trace=traceback.format_exc(),
            )
            raise

    async def _add_to_pending_list(self, artist_name: str) -> None:
        """Add an artist to the pending queue for later processing."""
        # Skip empty strings
        if not artist_name or not artist_name.strip():
            logger.debug("Skipping empty artist name")
            return

        await self.redis.sadd("pending:artists", artist_name)
        logger.debug(f"Added artist to pending queue: {artist_name}")

    async def _process_queued_artists(self) -> None:
        """Process artists queued during ingestion using Redis."""
        try:
            # Get all pending artist names from Redis
            artist_names = await self.redis.smembers(PENDING_ARTISTS_KEY)

            # Process each artist
            for artist_name in artist_names:
                try:
                    # Search for artist to get UUID
                    search_results = await self.soundcharts_service.search_artist(
                        artist_name,
                    )
                    if not search_results.get("items"):
                        logger.error("Artist not found", artist=artist_name)
                        continue

                    artist_data = search_results["items"][0]
                    artist_metadata = (
                        await self.soundcharts_service.get_artist_metadata(
                            artist_data["uuid"],
                        )
                    )
                    await self._process_artist_metadata(artist_metadata)
                except Exception as e:
                    logger.error(
                        "❌ Failed to process queued artist",
                        artist_name=artist_name,
                        error=str(e),
                        stack_trace=traceback.format_exc(),
                    )

            # Clear the pending list in Redis
            await self.redis.delete(PENDING_ARTISTS_KEY)
            logger.info("✅ Processed queued artists")
        except Exception as e:
            logger.error(
                "❌ Failed to process queued artists",
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

    async def _process_song_metadata(self, song_metadata: Dict) -> None:
        """Process song metadata and create nodes/relationships."""
        try:
            song_object = song_metadata["object"]

            # Create Track node and get internal ID
            internal_track_id = await self._create_track_node(song_object)

            # Process audio features if available and not None
            if "audio" in song_object and song_object["audio"] is not None:
                await self._process_audio_features(
                    song_object["audio"],
                    internal_track_id,
                )

            # Process all related entities using internal ID
            await self._process_related_entities(song_object, internal_track_id)

        except Exception as e:
            logger.error(
                "❌ Failed to process song metadata",
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

    async def _process_album_metadata(self, album_metadata: Dict) -> None:
        """Process album metadata with robust validation."""
        try:
            # Validate basic structure
            if not isinstance(album_metadata, dict):
                raise ValueError("Album data must be dictionary")

            # Extract the nested 'object' dictionary
            album_object = album_metadata.get("object", {})
            if not album_object:
                raise ValueError("Missing album object in metadata")

            # Extract required fields with defaults
            album_data = {
                "name": album_object.get("name", "Unknown Album"),
                "creditName": album_object.get("creditName", ""),
                "releaseDate": self._parse_release_date(
                    album_object.get("releaseDate"),
                ),
                "uuid": album_object.get("uuid"),
                "type": album_object.get("type", "album"),
                "upc": album_object.get("upc", ""),
                "totalTracks": album_object.get("totalTracks", 0),
                "imageUrl": album_object.get("imageUrl", ""),
            }

            # Validate required fields
            if not album_data["uuid"]:
                raise ValueError("Missing required field: uuid")

            # Process album
            internal_album_id = await self._create_album_node(album_data)

            # Process labels as separate nodes
            raw_labels = album_object.get("labels", [])
            for label in raw_labels:
                if label.get("name"):
                    await self._process_label(label, internal_album_id)

            # Process tracklisting with internal IDs
            tracklisting = await self.soundcharts_service.get_album_tracklisting(
                album_data["uuid"],
            )
            for track in tracklisting.get("tracks", []):
                # Create Track node and get internal ID
                internal_track_id = await self._create_track_node(track)

                # Create relationship using internal IDs
                await self._upsert_neo4j_relationship(
                    internal_album_id,
                    internal_track_id,
                    "CONTAINS",
                )

                # Process track relationships using internal ID
                await self._process_related_entities(track, internal_track_id)

            # Process album relationships using internal ID
            await self._process_related_entities(album_data, internal_album_id)

        except Exception as e:
            logger.error(
                "❌ Failed to process album metadata",
                error=str(e),
                album_data=album_metadata,
                stack_trace=traceback.format_exc(),
            )
            raise

    def _parse_release_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Safely parse release date from various formats."""
        if not date_str:
            return None

        try:
            # Handle ISO format
            if "T" in date_str:
                return datetime.fromisoformat(date_str)
            # Handle other formats as needed
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            logger.warning("Invalid date format", date_str=date_str)
            return None

    async def _process_artist_metadata(self, artist_metadata: Dict) -> None:
        """Process artist metadata and create nodes."""
        try:
            artist_object = artist_metadata["object"]

            # Create artist node and get internal ID
            internal_artist_id = await self._create_artist_node(artist_object)

            # Process related entities using internal ID
            await self._process_related_entities(artist_object, internal_artist_id)

        except Exception as e:
            logger.error(
                "❌ Failed to process artist metadata",
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

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
        await self._process_annotations(
            lyrics_metadata.get("annotations", []),
            lyrics_id,
        )

    async def _process_annotations(
        self,
        annotations: List[Dict],
        lyrics_id: str,
    ) -> None:
        """Process annotations for lyrics."""
        try:
            for annotation in annotations:
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
                logger.debug(
                    "✅ Processed annotation",
                    lyrics_id=lyrics_id,
                    annotation_id=annotation_node["id"],
                )
        except Exception as e:
            logger.error(
                "❌ Failed to process annotations",
                lyrics_id=lyrics_id,
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

    async def _process_audience_data(self, audience_data: Dict, artist_id: str) -> None:
        """Process audience data for an artist."""
        try:
            for platform, metrics in audience_data.items():
                audience_node = {
                    "id": f"audience_{artist_id}_{platform}",
                    "artist_id": artist_id,
                    "platform": platform,
                    "follower_count": metrics.get("follower_count"),
                    "following_count": metrics.get("following_count"),
                    "post_count": metrics.get("post_count"),
                    "view_count": metrics.get("view_count"),
                    "like_count": metrics.get("like_count"),
                }
                await self._upsert_neo4j_node("Audience", audience_node)
                logger.debug(
                    "✅ Processed audience data",
                    artist_id=artist_id,
                    platform=platform,
                )
        except Exception as e:
            logger.error(
                "❌ Failed to process audience data",
                artist_id=artist_id,
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

    async def _process_popularity_data(
        self,
        popularity_data: Dict,
        artist_id: str,
    ) -> None:
        """Process popularity metrics for an artist."""
        try:
            for platform, metrics in popularity_data.items():
                popularity_node = {
                    "id": f"popularity_{artist_id}_{platform}",
                    "artist_id": artist_id,
                    "platform": platform,
                    "date": metrics.get("date"),
                    "value": metrics.get("value"),
                }
                await self._upsert_neo4j_node("Popularity", popularity_node)
                logger.debug(
                    "✅ Processed popularity data",
                    artist_id=artist_id,
                    platform=platform,
                )
        except Exception as e:
            logger.error(
                "❌ Failed to process popularity data",
                artist_id=artist_id,
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

    async def _process_streaming_data(
        self,
        streaming_data: Dict,
        artist_id: str,
    ) -> None:
        """Process streaming metrics for an artist."""
        try:
            for platform, metrics in streaming_data.items():
                streaming_node = {
                    "id": f"streaming_{artist_id}_{platform}",
                    "artist_id": artist_id,
                    "platform": platform,
                    "date": metrics.get("date"),
                    "value": metrics.get("value"),
                }
                await self._upsert_neo4j_node("StreamingData", streaming_node)
                logger.debug(
                    "✅ Processed streaming data",
                    artist_id=artist_id,
                    platform=platform,
                )
        except Exception as e:
            logger.error(
                "❌ Failed to process streaming data",
                artist_id=artist_id,
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

    async def _process_lyrics_analysis(
        self,
        lyrics_analysis: Dict,
        track_id: str,
    ) -> None:
        """Process lyrics analysis for a track."""
        try:
            analysis_node = {
                "id": f"lyrics_analysis_{track_id}",
                "track_id": track_id,
                "themes": lyrics_analysis.get("themes"),
                "moods": lyrics_analysis.get("moods"),
                "cultural_reference_people": lyrics_analysis.get(
                    "cultural_reference_people",
                ),
                "cultural_reference_non_people": lyrics_analysis.get(
                    "cultural_reference_non_people",
                ),
                "brands": lyrics_analysis.get("brands"),
                "locations": lyrics_analysis.get("locations"),
                "narrative_style": lyrics_analysis.get("narrative_style"),
                "emotional_intensity_score": lyrics_analysis.get(
                    "emotional_intensity_score",
                ),
                "complexity_score": lyrics_analysis.get("complexity_score"),
                "repetitiveness_score": lyrics_analysis.get("repetitiveness_score"),
                "rhyme_scheme_score": lyrics_analysis.get("rhyme_scheme_score"),
                "imagery_score": lyrics_analysis.get("imagery_score"),
            }
            await self._upsert_neo4j_node("LyricsAnalysis", analysis_node)
            logger.debug("✅ Processed lyrics analysis", track_id=track_id)
        except Exception as e:
            logger.error(
                "❌ Failed to process lyrics analysis",
                track_id=track_id,
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

    async def _process_isrc_codes(self, isrc_data: Dict, track_id: str) -> None:
        """Process ISRC codes for a track."""
        try:
            for isrc in isrc_data:
                isrc_node = {
                    "id": f"isrc_{isrc['value']}",
                    "value": isrc["value"],
                    "country_code": isrc["country_code"],
                    "country_name": isrc["country_name"],
                }
                await self._upsert_neo4j_node("ISRC", isrc_node)
                await self._upsert_neo4j_relationship(
                    track_id,
                    isrc_node["id"],
                    "HAS_ISRC",
                )
                logger.debug(
                    "✅ Processed ISRC code",
                    track_id=track_id,
                    isrc=isrc["value"],
                )
        except Exception as e:
            logger.error(
                "❌ Failed to process ISRC codes",
                track_id=track_id,
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

    async def ingest_soundcharts_api(self, artist_name: str) -> Dict:
        """Ingest all SoundCharts data for an artist and build Neo4j graph."""
        try:
            logger.info("🎤 Starting artist ingestion", artist=artist_name)
            # Step 1: Search for artist and get UUID
            search_results = await self.soundcharts_service.search_artist(artist_name)
            if not search_results.get("items"):
                logger.error("Artist not found", artist=artist_name)
                return {"status": "skipped", "reason": "artist not found"}

            artist_data = search_results["items"][0]
            artist_id = artist_data["uuid"]
            logger.debug(
                "Found artist ID",
                artist_name=artist_name,
                artist_id=artist_id,
            )

            # Step 2: Get all artist metadata
            artist_metadata = await self.soundcharts_service.get_artist_metadata(
                artist_id,
            )
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

                # Process lyrics analysis
                lyrics_analysis = await self.soundcharts_service.get_lyrics_analysis(
                    song["uuid"],
                )
                await self._process_lyrics_analysis(lyrics_analysis, song["uuid"])

            # Step 5: Get and process artist albums
            albums = await self.soundcharts_service.get_artist_albums(artist_id)
            for album in albums.get("items", []):
                if not album.get("uuid"):
                    logger.error(
                        "Album missing UUID, skipping",
                        album=album,
                    )
                    continue

                album_metadata = await self.soundcharts_service.get_album_metadata(
                    album["uuid"],
                )
                await self._process_album_metadata(album_metadata)

            # Step 6: Get and process audience data
            audience_data = await self.soundcharts_service.get_artist_audience(
                artist_id,
            )
            await self._process_audience_data(audience_data, artist_id)

            # Step 7: Get and process popularity data
            popularity_data = await self.soundcharts_service.get_artist_popularity(
                artist_id,
            )
            await self._process_popularity_data(popularity_data, artist_id)

            # Step 8: Get and process streaming data
            streaming_data = await self.soundcharts_service.get_artist_streaming_data(
                artist_id,
            )
            await self._process_streaming_data(streaming_data, artist_id)

            # Return success status immediately
            result = {"status": "success", "artist_id": artist_id}

            return result
        except Exception as e:
            logger.error(
                "🚨 Ingestion failed",
                artist=artist_name,
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

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

    async def _create_track_node(self, track_data: Dict) -> str:
        """Create a Track node and return its internal UUID."""
        track = Track(
            id=f"track_{uuid.uuid4()}",  # Add prefix here
            soundcharts_uuid=track_data["uuid"],
            name=track_data["name"],
            credit_name=track_data.get("creditName"),
            release_date=track_data.get("releaseDate"),
            copyright=track_data.get("copyright"),
            app_url=track_data.get("appUrl"),
            image_url=track_data.get("imageUrl"),
            duration=track_data.get("duration"),
            explicit=track_data.get("explicit"),
            composers=track_data.get("composers"),
            producers=track_data.get("producers"),
            language_code=track_data.get("languageCode"),
        )
        await self._upsert_neo4j_node("Track", track.dict())
        return track.id

    async def _create_artist_node(self, artist_data: Dict) -> str:
        """Create an Artist node and return its internal UUID."""
        artist = Artist(
            id=f"artist_{uuid.uuid4()}",  # Add prefix here
            soundcharts_uuid=artist_data["uuid"],
            name=artist_data["name"],
            credit_name=artist_data.get("creditName"),
            country_code=artist_data.get("countryCode"),
            biography=artist_data.get("biography"),
            isni=artist_data.get("isni"),
            ipi=artist_data.get("ipi"),
            gender=artist_data.get("gender"),
            type=artist_data.get("type"),
            birth_date=artist_data.get("birthDate"),
        )
        await self._upsert_neo4j_node("Artist", artist.dict())
        return artist.id

    async def _create_album_node(self, album_data: Dict) -> str:
        """Create an Album node and return its internal UUID."""
        album = Album(
            id=f"album_{uuid.uuid4()}",  # Add prefix here
            soundcharts_uuid=album_data["uuid"],
            name=album_data["name"],
            credit_name=album_data.get("creditName"),
            upc=album_data.get("upc"),
            release_date=album_data.get("releaseDate"),
            total_tracks=album_data.get("totalTracks"),
            copyright=album_data.get("copyright"),
            image_url=album_data.get("imageUrl"),
        )
        await self._upsert_neo4j_node("Album", album.dict())
        return album.id

    async def _process_related_entities(
        self,
        entity_data: Dict,
        entity_id: str,
    ) -> None:
        """Process all related entities for a given entity."""
        try:
            # Process genres
            if "genres" in entity_data:
                for genre in entity_data["genres"]:
                    genre_id = f"genre_{sanitize_id_string(genre['root'])}"
                    genre_node = Genre(
                        id=genre_id,
                        root=genre["root"],
                        sub=genre.get("sub", []),
                    )
                    await self._upsert_neo4j_node("Genre", genre_node.dict())

                    await self._upsert_neo4j_relationship(
                        entity_id,
                        genre_id,
                        "HAS_GENRE",
                    )

            # Process platforms
            if "platforms" in entity_data:
                for platform in entity_data["platforms"]:
                    platform_node = Platform(
                        id=f"platform_{platform['code']}",
                        platform=platform["name"],
                    )
                    await self._upsert_neo4j_node("Platform", platform_node.dict())
                    await self._upsert_neo4j_relationship(
                        entity_id,
                        platform_node.id,
                        "ON_PLATFORM",
                    )

            # Process labels
            if "labels" in entity_data:
                for label in entity_data["labels"]:
                    label_node = Label(
                        id=f"label_{sanitize_id_string(label['name'])}",
                        name=label["name"],
                        type=label["type"],
                    )
                    await self._upsert_neo4j_node("Label", label_node.dict())
                    await self._upsert_neo4j_relationship(
                        entity_id,
                        label_node.id,
                        "HAS_LABEL",
                    )

            # Process producers and composers
            for role_type in ["producers", "composers"]:
                if role_type in entity_data:
                    for name in entity_data[role_type]:
                        # Check if artist exists first and get UUID
                        check_query = """
                        MATCH (n:Artist {name: $name}) 
                        RETURN n.id AS artist_id
                        """
                        async with self.neo4j_driver.session() as session:
                            result = await session.run(check_query, name=name)
                            record = await result.single()

                            if not record:
                                logger.debug(
                                    "Artist not found, adding to pending queue",
                                    name=name,
                                    role_type=role_type,
                                )
                                # Add to pending artists queue
                                await self._add_to_pending_list(name)
                                continue

                            internal_artist_id = record["artist_id"]

                            await self._upsert_neo4j_relationship(
                                entity_id,
                                internal_artist_id,
                                f"HAS_{role_type[:-1].upper()}",
                            )

            # Process featured artists
            if "featured_artists" in entity_data:
                for artist in entity_data["featured_artists"]:
                    await self._add_to_pending_list(artist["name"])
                    await self._upsert_neo4j_relationship(
                        artist["uuid"],
                        entity_id,
                        "FEATURED_ON",
                    )
        except Exception as e:
            logger.error(
                "❌ Failed to process related entities",
                error=str(e),
                stack_trace=traceback.format_exc(),
                entity_id=entity_id,
            )
            raise

    async def _process_platforms(self, platforms: List[Dict]) -> None:
        """Process platform data and create nodes."""
        logger.info("🖥️ Processing platforms", count=len(platforms))

        for platform in platforms:
            try:
                # Create platform model without explicitly passing 'id'
                platform_model = Platform(
                    **platform,  # Just unpack the dictionary
                )
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
            await self.deduplication_queue.close()
            await self.neo4j_driver.close()
            logger.info("✅ Resources closed successfully")
        except Exception as e:
            logger.error("❌ Failed to close resources", error=str(e))

    def _generate_composite_id(self, prefix: str, *parts: str) -> str:
        """Generate a consistent composite ID from parts."""
        if not parts:
            raise ValueError("At least one part is required for composite ID")

        clean_parts = []
        for part in parts:
            if not part:
                raise ValueError("Empty part in composite ID generation")
            # Use the shared sanitization function
            clean_part = sanitize_id_string(part).lower()
            clean_parts.append(clean_part)

        return f"{prefix}_{'_'.join(clean_parts)}"

    def _get_merge_key(self, label: str) -> str:
        """Get the merge key for a given label."""
        # Special cases for Artist, Track, and Album
        if label in ["Artist", "Track", "Album"]:
            return "soundcharts_uuid"

        # Default to "id" for all other nodes
        return "id"

    async def _create_lyrics_analysis_node(
        self,
        track_id: str,
        analysis_data: Dict,
    ) -> None:
        analysis = LyricsAnalysis(
            track_id=track_id,
            **analysis_data,
        )
        await self._upsert_neo4j_node("LyricsAnalysis", analysis.dict())

    async def _create_popularity_node(
        self,
        artist_id: str,
        platform: str,
        date: datetime,
        value: int,
    ) -> None:
        popularity = Popularity(
            artist_id=artist_id,
            platform=platform,
            date=date,
            value=value,
        )
        await self._upsert_neo4j_node("Popularity", popularity.dict())

    async def _process_artist_from_song(self, artist_data: dict, song_id: str) -> None:
        """Process artist data from song metadata."""
        try:
            if not isinstance(artist_data, dict):
                logger.warning(
                    "Invalid artist data in song object",
                    artist_data=artist_data,
                )
                return

            # Log incoming artist data
            logger.debug("Processing artist data", artist_data=artist_data)

            # Add artist to pending list
            await self._add_to_pending_list(artist_data["name"])

            # Create artist node
            artist = Artist(
                id=f"artist_{uuid.uuid4()}",
                soundcharts_uuid=artist_data["uuid"],
                name=artist_data["name"],
                slug=artist_data.get("slug"),
                app_url=artist_data.get("appUrl"),
                image_url=artist_data.get("imageUrl"),
            )

            # Log the artist model before upsert
            logger.debug("Created Artist model", artist=artist.dict())

            await self._upsert_neo4j_node("Artist", artist.dict())

            # Process artist relationships
            await self._upsert_neo4j_relationship(
                song_id,  # Song ID
                artist.id,  # Artist ID
                "HAS_ARTIST",
            )

        except Exception as e:
            logger.error("Failed to process artist from song metadata", error=str(e))
            raise

    async def _process_platform_ids(self, platform_ids: Dict, artist_id: str) -> None:
        """Process platform IDs for an artist."""
        try:
            for platform, identifier in platform_ids.items():
                # Create platform relationship
                await self._upsert_neo4j_relationship(
                    artist_id,
                    platform,
                    "ON_PLATFORM",
                    properties={"identifier": identifier},
                )
                logger.debug(
                    "✅ Created platform relationship",
                    artist_id=artist_id,
                    platform=platform,
                )
        except Exception as e:
            logger.error(
                "❌ Failed to process platform IDs",
                artist_id=artist_id,
                error=str(e),
            )
            raise

    async def _neo4j_node_exists(self, node_id: str) -> bool:
        """Check if a node exists in Neo4j."""
        try:
            result = await self.neo4j_driver.execute_query(
                "MATCH (n {id: $node_id}) RETURN count(n) AS count",
                node_id=node_id,
            )
            return result.records[0]["count"] > 0
        except Exception as e:
            logger.error(
                "Failed to check node existence",
                node_id=node_id,
                error=str(e),
            )
            return False

    async def _process_label(self, label_data: Dict, album_id: str) -> None:
        """Process label data and create relationship to album."""
        try:
            # Create label node with generated ID
            label_name = label_data.get("name")
            if not label_name:
                logger.warning("Label missing name, skipping", label=label_data)
                return

            label_id = f"label_{sanitize_id_string(label_name)}"

            # Check if label node exists, create if not
            if not await self._neo4j_node_exists(label_id):
                label_node = {
                    "id": label_id,
                    "name": label_name,
                    "type": label_data.get("type"),
                }
                await self._upsert_neo4j_node("Label", label_node)
                logger.debug("✅ Created label node", label_id=label_id)

            # Create relationship between album and label
            await self._upsert_neo4j_relationship(
                album_id,
                label_id,
                "HAS_LABEL",
            )
            logger.debug(
                "✅ Created label relationship",
                album_id=album_id,
                label_id=label_id,
            )
        except Exception as e:
            logger.error(
                "❌ Failed to process label",
                label=label_data,
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

    async def _process_audio_features(
        self,
        audio_features: Dict,
        track_id: str,
    ) -> None:
        """Process audio features for a track."""
        try:
            audio_node = {
                "id": f"audio_{track_id}",
                "danceability": audio_features.get("danceability"),
                "energy": audio_features.get("energy"),
                "key": audio_features.get("key"),
                "loudness": audio_features.get("loudness"),
                "mode": audio_features.get("mode"),
                "speechiness": audio_features.get("speechiness"),
                "acousticness": audio_features.get("acousticness"),
                "instrumentalness": audio_features.get("instrumentalness"),
                "liveness": audio_features.get("liveness"),
                "valence": audio_features.get("valence"),
                "tempo": audio_features.get("tempo"),
                "time_signature": audio_features.get("time_signature"),
            }
            await self._upsert_neo4j_node("Audio", audio_node)
            logger.debug("✅ Processed audio features", track_id=track_id)
        except Exception as e:
            logger.error(
                "❌ Failed to process audio features",
                track_id=track_id,
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

    async def _process_roles(self, roles: List[Dict], track_id: str) -> None:
        """Process roles for a track."""
        try:
            for role in roles:
                role_node = {
                    "id": f"role_{sanitize_id_string(role['name'])}",
                    "name": role["name"],
                }
                await self._upsert_neo4j_node("Role", role_node)
                await self._upsert_neo4j_relationship(
                    track_id,
                    role_node["id"],
                    "HAS_ROLE",
                )
                logger.debug("✅ Processed role", track_id=track_id, role=role["name"])
        except Exception as e:
            logger.error(
                "❌ Failed to process roles",
                track_id=track_id,
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise

    async def get_pending_artists(self) -> List[str]:
        """Get the list of pending artists from Redis."""
        return await self.redis.smembers(PENDING_ARTISTS_KEY)
