import asyncio
import time
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

        # Add this after initializing neo4j_driver
        await self._add_unique_constraints()
        logger.info("✅ Neo4j constraints ensured")

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

            # Check deduplication queue using soundcharts_uuid
            if "soundcharts_uuid" in properties:
                if await self.deduplication_queue.is_processed(
                    properties["soundcharts_uuid"],
                ):
                    logger.debug(
                        "Node already processed",
                        label=label,
                        soundcharts_uuid=properties["soundcharts_uuid"],
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
                    timeout=60,
                )
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

    async def _add_to_pending_list(
        self,
        artist_name: str,
        soundcharts_uuid: str,
    ) -> None:
        """Add an artist to the pending queue for later processing."""
        # Skip empty strings
        if not artist_name or not artist_name.strip() or not soundcharts_uuid:
            logger.debug("Skipping empty artist name or UUID")
            return

        # Check if artist is already in the queue
        value = f"{artist_name}|{soundcharts_uuid}"
        score = await self.redis.zscore("pending:artists", value)
        if score is not None:
            logger.debug(f"Artist already in queue: {artist_name} ({soundcharts_uuid})")
            return

        # Add artist with initial score of 0
        # The score will be updated when we sort by popularity
        await self.redis.zadd("pending:artists", {value: 0})
        logger.debug(
            f"Added artist to pending queue: {artist_name} ({soundcharts_uuid})",
        )

    async def _process_song_metadata(self, song_metadata: Dict) -> None:
        """Process song metadata and create nodes."""
        try:
            song_object = song_metadata["object"]

            # First create the track node
            track_id = await self._create_track_node(song_object)

            # Then process all related entities including audio features
            await self._process_related_entities(song_object, track_id)

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

    async def _process_artist_metadata(
        self,
        artist_metadata: Dict,
        weight: float = 0,
    ) -> None:
        """Process artist metadata and create nodes."""
        try:
            logger.debug("Processing artist metadata", metadata=artist_metadata)

            # Verify the artist object exists
            artist_object = artist_metadata.get("object")
            if not artist_object:
                logger.error("Missing artist object in metadata")
                return

            logger.debug("Artist object found", artist_object=artist_object)

            # Verify required fields
            if "uuid" not in artist_object:
                logger.error("Missing required field: uuid")
                return

            # Add weight to artist data
            artist_object["weight"] = weight

            # Create artist node and get internal ID
            internal_artist_id = await self._create_artist_node(artist_object)
            logger.debug("Created artist node", artist_id=internal_artist_id)

            # Process related entities using internal ID
            await self._process_related_entities(artist_object, internal_artist_id)
            logger.debug(
                "Processed related entities for artist",
                artist_id=internal_artist_id,
            )

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

    async def ingest_soundcharts_api(
        self,
        soundcharts_uuid: str,
        weight: float = 0,
    ) -> Dict:
        """Ingest all SoundCharts data for an artist and build Neo4j graph."""
        try:
            # Get artist metadata to include name in logs
            artist_metadata = await self.soundcharts_service.get_artist_metadata(
                soundcharts_uuid,
            )
            if not artist_metadata:
                logger.error("Artist not found", soundcharts_uuid=soundcharts_uuid)
                return {"status": "skipped", "reason": "artist not found"}

            artist_name = artist_metadata["object"].get("name", "Unknown Artist")
            logger.info(
                "🎤 Starting artist ingestion",
                artist_name=artist_name,
                soundcharts_uuid=soundcharts_uuid,
                weight=weight,
            )

            await self._process_artist_metadata(artist_metadata, weight)

            # Process songs
            songs = await self.soundcharts_service.get_artist_songs(soundcharts_uuid)
            logger.debug(
                "Processing artist songs",
                artist_name=artist_name,
                soundcharts_uuid=soundcharts_uuid,
                count=len(songs.get("items", [])),
            )
            for song in songs.get("items", []):
                song_metadata = await self.soundcharts_service.get_song_metadata(
                    song["uuid"],
                )
                await self._process_song_metadata(song_metadata)

            # Process albums
            albums = await self.soundcharts_service.get_artist_albums(soundcharts_uuid)
            logger.debug(
                "Processing artist albums",
                artist_name=artist_name,
                soundcharts_uuid=soundcharts_uuid,
                count=len(albums.get("items", [])),
            )
            for album in albums.get("items", []):
                if not album.get("uuid"):
                    logger.error(
                        "Album missing UUID, skipping",
                        artist_name=artist_name,
                        soundcharts_uuid=soundcharts_uuid,
                    )
                    continue

                album_metadata = await self.soundcharts_service.get_album_metadata(
                    album["uuid"],
                )
                await self._process_album_metadata(album_metadata)

            # Return success status
            result = {
                "status": "success",
                "artist_name": artist_name,
                "soundcharts_uuid": soundcharts_uuid,
                "weight": weight,
            }

            logger.info(
                "✅ Successfully processed artist",
                artist_name=artist_name,
                soundcharts_uuid=soundcharts_uuid,
                weight=weight,
            )
            return result

        except Exception as e:
            logger.error(
                "🚨 Ingestion failed",
                artist_name=artist_name,
                soundcharts_uuid=soundcharts_uuid,
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
        soundcharts_uuid = track_data["uuid"]

        # Check deduplication queue first
        if await self.deduplication_queue.is_processed(soundcharts_uuid):
            logger.debug("Track already processed", soundcharts_uuid=soundcharts_uuid)
            return await self._get_track_id_by_uuid(soundcharts_uuid)

        track = Track(
            id=f"track_{uuid.uuid4()}",
            soundcharts_uuid=soundcharts_uuid,
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

        # Use transaction to ensure node exists
        async with self.neo4j_driver.session() as session:
            await session.execute_write(
                lambda tx: tx.run(
                    """
                    MERGE (t:Track {soundcharts_uuid: $uuid})
                    ON CREATE SET t = $props
                    ON MATCH SET t += $update_props, 
                                 t.last_updated = $now
                    """,
                    uuid=soundcharts_uuid,
                    props=track.dict(),
                    update_props={k: v for k, v in track.dict().items() if k != "id"},
                    now=datetime.utcnow(),
                ),
            )

            # Verify node existence in the same transaction
            result = await session.run(
                "MATCH (t:Track {soundcharts_uuid: $uuid}) RETURN t.id AS track_id",
                uuid=soundcharts_uuid,
            )
            record = await result.single()
            created_id = record["track_id"]

        # Only mark processed after successful creation
        await self.deduplication_queue.mark_processed(soundcharts_uuid)
        return created_id

    async def _get_track_id_by_uuid(self, soundcharts_uuid: str) -> Optional[str]:
        """Get track ID by soundcharts_uuid if it exists."""
        try:
            query = """
            MATCH (t:Track {soundcharts_uuid: $uuid})
            RETURN t.id AS track_id
            """
            async with self.neo4j_driver.session() as session:
                result = await session.run(query, uuid=soundcharts_uuid)
                record = await result.single()
                return record["track_id"] if record else None
        except Exception as e:
            logger.error(
                "Failed to get track by UUID",
                uuid=soundcharts_uuid,
                error=str(e),
            )
            return None

    async def _create_artist_node(self, artist_data: Dict) -> str:
        """Create an Artist node and return its internal UUID."""
        soundcharts_uuid = artist_data["uuid"]

        # Check deduplication queue first
        if await self.deduplication_queue.is_processed(soundcharts_uuid):
            logger.debug("Artist already processed", soundcharts_uuid=soundcharts_uuid)
            return await self._get_artist_id_by_uuid(soundcharts_uuid)

        artist = Artist(
            id=f"artist_{uuid.uuid4()}",
            soundcharts_uuid=soundcharts_uuid,
            name=artist_data["name"],
            credit_name=artist_data.get("creditName"),
            country_code=artist_data.get("countryCode"),
            biography=artist_data.get("biography"),
            isni=artist_data.get("isni"),
            ipi=artist_data.get("ipi"),
            gender=artist_data.get("gender"),
            type=artist_data.get("type"),
            birth_date=artist_data.get("birthDate"),
            weight=artist_data.get("weight", 0.0),
        )

        # Use transaction to ensure node exists
        async with self.neo4j_driver.session() as session:
            await session.execute_write(
                lambda tx: tx.run(
                    """
                    MERGE (a:Artist {soundcharts_uuid: $uuid})
                    ON CREATE SET a = $props
                    ON MATCH SET a += $update_props, 
                                 a.last_updated = $now
                    """,
                    uuid=soundcharts_uuid,
                    props=artist.dict(),
                    update_props={k: v for k, v in artist.dict().items() if k != "id"},
                    now=datetime.utcnow(),
                ),
            )

            # Verify node existence in the same transaction
            result = await session.run(
                "MATCH (a:Artist {soundcharts_uuid: $uuid}) RETURN a.id AS artist_id",
                uuid=soundcharts_uuid,
            )
            record = await result.single()
            created_id = record["artist_id"]

        # Only mark processed after successful creation
        await self.deduplication_queue.mark_processed(soundcharts_uuid)
        return created_id

    async def _create_album_node(self, album_data: Dict) -> str:
        """Create an Album node and return its internal UUID."""
        soundcharts_uuid = album_data["uuid"]

        # Check deduplication queue first
        if await self.deduplication_queue.is_processed(soundcharts_uuid):
            logger.debug("Album already processed", soundcharts_uuid=soundcharts_uuid)
            return await self._get_album_id_by_uuid(soundcharts_uuid)

        album = Album(
            id=f"album_{uuid.uuid4()}",
            soundcharts_uuid=soundcharts_uuid,
            name=album_data["name"],
            credit_name=album_data.get("creditName"),
            upc=album_data.get("upc"),
            release_date=album_data.get("releaseDate"),
            total_tracks=album_data.get("totalTracks"),
            copyright=album_data.get("copyright"),
            image_url=album_data.get("imageUrl"),
        )

        # Use transaction to ensure node exists
        async with self.neo4j_driver.session() as session:
            await session.execute_write(
                lambda tx: tx.run(
                    """
                    MERGE (a:Album {soundcharts_uuid: $uuid})
                    ON CREATE SET a = $props
                    ON MATCH SET a += $update_props, 
                                 a.last_updated = $now
                    """,
                    uuid=soundcharts_uuid,
                    props=album.dict(),
                    update_props={k: v for k, v in album.dict().items() if k != "id"},
                    now=datetime.utcnow(),
                ),
            )

            # Verify node existence in the same transaction
            result = await session.run(
                "MATCH (a:Album {soundcharts_uuid: $uuid}) RETURN a.id AS album_id",
                uuid=soundcharts_uuid,
            )
            record = await result.single()
            created_id = record["album_id"]

        # Only mark processed after successful creation
        await self.deduplication_queue.mark_processed(soundcharts_uuid)
        return created_id

    async def _get_album_id_by_uuid(self, soundcharts_uuid: str) -> Optional[str]:
        """Get album ID by soundcharts_uuid if it exists."""
        try:
            query = """
            MATCH (a:Album {soundcharts_uuid: $uuid})
            RETURN a.id AS album_id
            """
            async with self.neo4j_driver.session() as session:
                result = await session.run(query, uuid=soundcharts_uuid)
                record = await result.single()
                return record["album_id"] if record else None
        except Exception as e:
            logger.error(
                "Failed to get album by UUID",
                uuid=soundcharts_uuid,
                error=str(e),
            )
            return None

    async def _process_related_entities(
        self,
        entity_data: Dict,
        entity_id: str,
    ) -> None:
        """Process all related entities for a given entity."""
        try:
            logger.debug("Starting to process related entities", entity_id=entity_id)

            # Log all available data
            logger.debug("Entity data keys", keys=list(entity_data.keys()))

            # Process audio features if available
            if "audio" in entity_data and entity_data["audio"] is not None:
                logger.debug("Processing audio features", entity_id=entity_id)
                audio_node = {
                    "id": f"audio_{entity_id}",
                    "danceability": entity_data["audio"].get("danceability"),
                    "energy": entity_data["audio"].get("energy"),
                    "key": entity_data["audio"].get("key"),
                    "loudness": entity_data["audio"].get("loudness"),
                    "mode": entity_data["audio"].get("mode"),
                    "speechiness": entity_data["audio"].get("speechiness"),
                    "acousticness": entity_data["audio"].get("acousticness"),
                    "instrumentalness": entity_data["audio"].get("instrumentalness"),
                    "liveness": entity_data["audio"].get("liveness"),
                    "valence": entity_data["audio"].get("valence"),
                    "tempo": entity_data["audio"].get("tempo"),
                    "time_signature": entity_data["audio"].get("time_signature"),
                }
                await self._upsert_neo4j_node("Audio", audio_node)
                await self._upsert_neo4j_relationship(
                    entity_id,
                    audio_node["id"],
                    "HAS_AUDIO_FEATURES",
                )
                await self._upsert_neo4j_relationship(
                    audio_node["id"],
                    entity_id,
                    "AUDIO_FEATURES_FOR",
                )
                logger.debug("✅ Processed audio features", entity_id=entity_id)

            # Process album artists if available
            if "artists" in entity_data:
                logger.debug(
                    "Processing artists",
                    entity_id=entity_id,
                    count=len(entity_data["artists"]),
                )
                for artist in entity_data["artists"]:
                    # Use proper artist creation method
                    artist_id = await self._create_artist_node(
                        {
                            "uuid": artist["uuid"],
                            "name": artist["name"],
                            "creditName": artist.get("creditName"),
                        },
                    )

                    # Create relationship between entity and artist
                    await self._upsert_neo4j_relationship(
                        entity_id,
                        artist_id,
                        "HAS_ARTIST",
                    )
                    await self._upsert_neo4j_relationship(
                        artist_id,
                        entity_id,
                        "ARTIST_OF",
                    )

                    # Add artist to pending list
                    await self._add_to_pending_list(artist.get("name"), artist["uuid"])

                    logger.debug(
                        "✅ Processed album artist",
                        entity_id=entity_id,
                        artist_id=artist_id,
                    )

            # Process genres
            if "genres" in entity_data:
                logger.debug(
                    "Processing genres",
                    entity_id=entity_id,
                    count=len(entity_data["genres"]),
                )
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
                    await self._upsert_neo4j_relationship(
                        genre_id,
                        entity_id,
                        "GENRE_OF",
                    )

            # Process platforms
            if "platforms" in entity_data:
                logger.debug(
                    "Processing platforms",
                    entity_id=entity_id,
                    count=len(entity_data["platforms"]),
                )
                for platform in entity_data["platforms"]:
                    platform_node = Platform(
                        id=f"platform_{platform['id']}",
                        platform=platform["platform"],
                    )
                    await self._upsert_neo4j_node("Platform", platform_node.dict())
                    await self._upsert_neo4j_relationship(
                        entity_id,
                        platform_node.id,
                        "ON_PLATFORM",
                    )
                    await self._upsert_neo4j_relationship(
                        platform_node.id,
                        entity_id,
                        "HOSTS",
                    )

            # Process labels
            if "labels" in entity_data:
                logger.debug(
                    "Processing labels",
                    entity_id=entity_id,
                    count=len(entity_data["labels"]),
                )
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
                    await self._upsert_neo4j_relationship(
                        label_node.id,
                        entity_id,
                        "LABEL_FOR",
                    )

            # Process producers and composers
            for role_type in ["producers", "composers"]:
                if role_type in entity_data:
                    logger.debug(
                        f"Processing {role_type}",
                        entity_id=entity_id,
                        count=len(entity_data[role_type]),
                    )
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
                                continue

                            internal_artist_id = record["artist_id"]

                            await self._upsert_neo4j_relationship(
                                entity_id,
                                internal_artist_id,
                                f"HAS_{role_type[:-1].upper()}",
                            )
                            await self._upsert_neo4j_relationship(
                                internal_artist_id,
                                entity_id,
                                f"{role_type[:-1].upper()}_OF",
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
                # Create platform model with prefixed ID
                platform_model = Platform(
                    id=f"platform_{platform['id']}",  # Add prefix here
                    platform=platform["platform"],
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
            if self.deduplication_queue:
                try:
                    await self.deduplication_queue.close()
                except Exception as e:
                    logger.warning("Error closing deduplication queue", error=str(e))

            if self.neo4j_driver:
                try:
                    await self.neo4j_driver.close()
                except Exception as e:
                    logger.warning("Error closing Neo4j driver", error=str(e))

            if self.redis:
                try:
                    await self.redis.close()
                except Exception as e:
                    logger.warning("Error closing Redis connection", error=str(e))

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

            # Check if artist has already been processed
            if await self.deduplication_queue.is_processed(artist_data["uuid"]):
                logger.debug(
                    "Artist already processed",
                    soundcharts_uuid=artist_data["uuid"],
                )
                return

            # Create artist node
            artist = Artist(
                id=f"artist_{uuid.uuid4()}",
                soundcharts_uuid=artist_data["uuid"],
                name=artist_data["name"],
                slug=artist_data.get("slug"),
                app_url=artist_data.get("appUrl"),
                image_url=artist_data.get("imageUrl"),
            )
            await self._upsert_neo4j_node("Artist", artist.dict())
            await self.deduplication_queue.mark_processed(artist_data["uuid"])

            # Process artist relationships
            await self._upsert_neo4j_relationship(
                song_id,  # Song ID
                artist.id,  # Artist ID
                "HAS_ARTIST",
            )
            await self._upsert_neo4j_relationship(
                artist.id,
                song_id,
                "ARTIST_OF",
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
                await self._upsert_neo4j_relationship(
                    platform,
                    artist_id,
                    "HOSTS",
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
            await self._upsert_neo4j_relationship(
                label_id,
                album_id,
                "LABEL_FOR",
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

    async def _get_artist_id_by_uuid(self, soundcharts_uuid: str) -> Optional[str]:
        """Get artist ID by soundcharts_uuid if it exists."""
        try:
            query = """
            MATCH (a:Artist {soundcharts_uuid: $uuid})
            RETURN a.id AS artist_id
            """
            async with self.neo4j_driver.session() as session:
                result = await session.run(query, uuid=soundcharts_uuid)
                record = await result.single()
                return record["artist_id"] if record else None
        except Exception as e:
            logger.error(
                "Failed to get artist by UUID",
                uuid=soundcharts_uuid,
                error=str(e),
            )
            return None

    async def process_pending_artists(self) -> None:
        """Process artists from the pending queue, sorted by streaming popularity."""
        try:
            while True:
                # Resort the entire list before processing each artist
                await self.sort_pending_artists_by_popularity()

                # Get the highest priority artist from the sorted set
                artist_value = await self.redis.zrevrange(
                    "pending:artists",
                    0,
                    0,
                    withscores=True,
                )
                if not artist_value:
                    logger.debug("🏁 Artist queue is empty")
                    break

                # Split the stored value into name and UUID, and get the score
                artist_name, soundcharts_uuid = artist_value[0][0].split("|")
                weight = artist_value[0][1]  # Get the score as weight
                logger.debug(
                    f"🔁 Processing artist: {artist_name} ({soundcharts_uuid}) with weight {weight}",
                )

                try:
                    # Pass weight to ingestion
                    result = await self.ingest_soundcharts_api(
                        soundcharts_uuid,
                        weight=weight,
                    )

                    if result["status"] == "success":
                        logger.info(
                            "✅ Successfully processed artist",
                            artist_name=artist_name,
                            soundcharts_uuid=soundcharts_uuid,
                            weight=weight,
                        )
                    else:
                        logger.error(
                            "❌ Failed to process artist",
                            artist_name=artist_name,
                            soundcharts_uuid=soundcharts_uuid,
                            error=result.get("error", "Unknown error"),
                        )

                    # Remove the processed artist from the sorted set
                    await self.redis.zrem("pending:artists", artist_value[0][0])

                except Exception as e:
                    logger.error(
                        "❌ Error processing artist",
                        artist_name=artist_name,
                        soundcharts_uuid=soundcharts_uuid,
                        error=str(e),
                    )
                    # Optionally, you could move failed artists to a separate set for retry
                    await self.redis.zadd(
                        "failed:artists",
                        {artist_value[0][0]: time.time()},
                    )
                    await self.redis.zrem("pending:artists", artist_value[0][0])

                # Optional: Add delay between processing if needed
                await asyncio.sleep(1)

            logger.info("🎉 All artists processed successfully")
        except asyncio.CancelledError:
            logger.info("Shutting down gracefully...")

    async def sort_pending_artists_by_popularity(self) -> None:
        """Resort the pending artist list based on streaming popularity."""
        try:
            logger.info("🔄 Resorting pending artists by streaming popularity")

            # Get all artists from the pending queue
            artists = await self.redis.zrange("pending:artists", 0, -1, withscores=True)
            logger.debug("Found artists in queue", count=len(artists))

            # Create a dictionary to store artist streaming scores
            streaming_scores = {}

            # Fetch streaming data for each artist
            for artist_value, _ in artists:
                artist_name, soundcharts_uuid = artist_value.split("|")
                logger.debug(
                    "Processing artist",
                    artist_name=artist_name,
                    soundcharts_uuid=soundcharts_uuid,
                )

                # Get streaming data from SoundCharts
                streaming_data = (
                    await self.soundcharts_service.get_artist_streaming_data(
                        soundcharts_uuid,
                    )
                )
                logger.debug(
                    "Received streaming data",
                    artist_name=artist_name,
                    platforms=list(streaming_data.keys()),
                )

                # Calculate an overall streaming score using the highest platform value
                max_value = 0
                max_platform = None

                for platform_code, platform_response in streaming_data.items():
                    logger.debug(
                        "Processing platform",
                        artist_name=artist_name,
                        platform=platform_code,
                    )

                    if not platform_response:
                        logger.debug(
                            "Empty platform response",
                            artist_name=artist_name,
                            platform=platform_code,
                        )
                        continue

                    if "items" not in platform_response:
                        logger.debug(
                            "Missing items in platform response",
                            artist_name=artist_name,
                            platform=platform_code,
                        )
                        continue

                    if not platform_response["items"]:
                        logger.debug(
                            "Empty items array in platform response",
                            artist_name=artist_name,
                            platform=platform_code,
                        )
                        continue

                    # Get the most recent value for this platform
                    most_recent = platform_response["items"][-1]
                    platform_value = most_recent["value"]
                    logger.debug(
                        "Platform value",
                        artist_name=artist_name,
                        platform=platform_code,
                        value=platform_value,
                        date=most_recent["date"],
                    )

                    if platform_value > max_value:
                        max_value = platform_value
                        max_platform = platform_code
                        logger.debug(
                            "New max value found",
                            artist_name=artist_name,
                            platform=platform_code,
                            value=platform_value,
                        )

                streaming_scores[artist_value] = max_value
                logger.info(
                    "Calculated final streaming score",
                    artist_name=artist_name,
                    score=max_value,
                    platform=max_platform,
                )

            # Remove all artists from the current queue
            await self.redis.delete("pending:artists")
            logger.debug("Cleared existing artist queue")

            # Add artists back with their streaming scores
            for artist_value, streaming_score in streaming_scores.items():
                await self.redis.zadd(
                    "pending:artists",
                    {artist_value: streaming_score},
                )
                logger.debug(
                    "Added artist to queue with score",
                    artist=artist_value.split("|")[0],
                    score=streaming_score,
                )

            logger.info(
                "✅ Successfully resorted pending artists by streaming popularity",
            )

        except Exception as e:
            logger.error(
                "❌ Failed to resort pending artists by streaming popularity",
                error=str(e),
                stack_trace=traceback.format_exc(),
            )
            raise
