import fcntl
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import httpx
from neo4j import AsyncGraphDatabase
from structlog import get_logger

from ..models import (
    ISRC,
    Album,
    Artist,
    Audience,
    Audio,
    Genre,
    Label,
    LyricsAnalysis,
    Platform,
    Popularity,
    Role,
    StreamingData,
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

    async def startup(self) -> None:
        """Perform asynchronous initialization tasks."""
        try:
            await self._add_unique_constraints()
        except Exception as e:
            logger.error("❌ Failed to add unique constraints", error=str(e))
            raise

    async def _add_unique_constraints(self) -> None:
        """Add unique constraints to Neo4j if they don't already exist."""
        constraints = [
            ("Artist", "soundcharts_uuid"),
            ("Track", "soundcharts_uuid"),
            ("Album", "soundcharts_uuid"),
            ("Genre", "id"),
            ("Label", "name"),
            ("Role", "id"),
            ("Platform", "id"),
            ("Audience", "id"),
            ("Popularity", "id"),
            ("StreamingData", "id"),
            ("LyricsAnalysis", "id"),
            ("ISRC", "value"),
            ("Audio", "id"),
            ("Artist", "id"),
            ("Track", "id"),
            ("Album", "id"),
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
            logger.debug("Upserting node", label=label, id=properties.get("id"))

            # Validate model based on label
            model_classes = {
                "Artist": Artist,
                "Track": Track,
                "Album": Album,
                "Genre": Genre,
                "Label": Label,
                "Role": Role,
                "Platform": Platform,
                "Audience": Audience,
                "Popularity": Popularity,
                "StreamingData": StreamingData,
                "LyricsAnalysis": LyricsAnalysis,
                "ISRC": ISRC,
                "Audio": Audio,
            }

            if label not in model_classes:
                raise ValueError(f"Invalid label: {label}")

            model_classes[label](**properties)

            # Get merge key and execute query
            merge_key = self._get_merge_key(label)
            query = f"MERGE (n:{label} {{{merge_key}: ${merge_key}}}) SET n += $props"

            async with self.neo4j_driver.session() as session:
                await session.run(
                    query,
                    **{merge_key: properties[merge_key]},
                    props=properties,
                )

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
        try:
            # Add validation for song_metadata structure
            if not song_metadata:
                logger.error("❌ Empty song metadata received")
                raise ValueError("Empty song metadata")

            if song_metadata.get("errors"):
                logger.error(
                    "❌ Errors in song metadata response",
                    errors=song_metadata["errors"],
                )
                raise ValueError(f"API errors: {song_metadata['errors']}")

            if "object" not in song_metadata:
                logger.error(
                    "❌ Invalid song metadata structure: missing 'object' key",
                    metadata=song_metadata,
                )
                raise ValueError("Invalid song metadata: missing 'object' key")

            song_object = song_metadata["object"]

            # Validate required fields in song_object
            required_fields = ["uuid", "name"]
            for field in required_fields:
                if field not in song_object:
                    logger.error(
                        "❌ Missing required field in song object",
                        field=field,
                        song_object=song_object,
                    )
                    raise ValueError(f"Song object missing required field: {field}")

            soundcharts_song_id = song_object["uuid"]  # SoundCharts UUID

            # Create Track node
            await self._create_track_node(song_object)

            # Process all related entities (including artists)
            await self._process_related_entities(song_object, soundcharts_song_id)

        except Exception as e:
            logger.error(
                "❌ Failed to process song metadata",
                error=str(e),
                song_metadata=song_metadata,
            )
            raise

    async def _process_album_metadata(self, album_metadata: Dict) -> None:
        """Process album metadata and create nodes/relationships."""
        album_object = album_metadata["object"]
        soundcharts_album_id = album_object["uuid"]  # SoundCharts UUID

        # Create Album node
        album_node = {
            "id": str(uuid.uuid4()),  # Our own UUIDv4
            "title": album_object["name"],
            "release_date": album_object["release_date"],
            "upc": album_object["upc"],
            "label": album_object["label"],
            "type": album_object["type"],
            "track_count": album_object["track_count"],
            "soundcharts": {
                "uuid": soundcharts_album_id,  # Store SoundCharts UUID
            },
        }
        await self._upsert_neo4j_node("Album", album_node)

        # Process related entities
        await self._process_related_entities(album_object, soundcharts_album_id)

        # Process tracklisting
        tracklisting = await self.soundcharts_service.get_album_tracklisting(
            soundcharts_album_id,
        )
        for track in tracklisting["tracks"]:
            soundcharts_track_id = track["uuid"]  # SoundCharts UUID
            self._add_to_pending_list("tracks", soundcharts_track_id)
            await self._upsert_neo4j_relationship(
                soundcharts_album_id,
                soundcharts_track_id,
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

    async def _process_audience_data(
        self,
        artist_id: str,
        platform: str,
        audience_data: Dict,
    ) -> None:
        """Process audience data and create nodes."""
        for item in audience_data["items"]:
            audience_id = f"audience_{artist_id}_{platform}_{item['date']}"
            audience_model = Audience(
                id=audience_id,
                artist_id=artist_id,
                platform=platform,
                date=item["date"],
                follower_count=item.get("followerCount"),
                following_count=item.get("followingCount"),
                post_count=item.get("postCount"),
                view_count=item.get("viewCount"),
                like_count=item.get("likeCount"),
            )
            await self._upsert_neo4j_node("Audience", audience_model.dict())
            await self._upsert_neo4j_relationship(
                artist_id,
                audience_id,
                "HAS_AUDIENCE",
            )
            await self._upsert_neo4j_relationship(
                platform,
                audience_id,
                "ON_PLATFORM",
            )

    async def _process_popularity_data(
        self,
        artist_id: str,
        platform: str,
        popularity_data: Dict,
    ) -> None:
        """Process popularity data and create nodes."""
        for item in popularity_data["items"]:
            popularity_id = f"popularity_{artist_id}_{platform}_{item['date']}"
            popularity_model = Popularity(
                id=popularity_id,
                artist_id=artist_id,
                platform=platform,
                date=item["date"],
                value=item.get("value"),
            )
            await self._upsert_neo4j_node("Popularity", popularity_model.dict())
            await self._upsert_neo4j_relationship(
                artist_id,
                popularity_id,
                "HAS_POPULARITY",
            )
            await self._upsert_neo4j_relationship(
                platform,
                popularity_id,
                "ON_PLATFORM",
            )

    async def _process_streaming_data(
        self,
        artist_id: str,
        platform: str,
        streaming_data: Dict,
    ) -> None:
        """Process streaming data and create nodes."""
        for item in streaming_data["items"]:
            streaming_id = f"streaming_{artist_id}_{platform}_{item['date']}"
            streaming_model = StreamingData(
                id=streaming_id,
                artist_id=artist_id,
                platform=platform,
                date=item["date"],
                value=item.get("value"),
            )
            await self._upsert_neo4j_node("StreamingData", streaming_model.dict())
            await self._upsert_neo4j_relationship(
                artist_id,
                streaming_id,
                "HAS_STREAMING",
            )
            await self._upsert_neo4j_relationship(
                platform,
                streaming_id,
                "ON_PLATFORM",
            )

    async def _process_lyrics_analysis(
        self,
        track_id: str,
        lyrics_analysis: Dict,
    ) -> None:
        """Process lyrics analysis data and create nodes."""
        analysis_model = LyricsAnalysis(
            id=f"lyrics_analysis_{track_id}",
            themes=lyrics_analysis.get("themes", []),
            moods=lyrics_analysis.get("moods", []),
            cultural_reference_people=lyrics_analysis.get(
                "culturalReferencePeople",
                [],
            ),
            cultural_reference_non_people=lyrics_analysis.get(
                "culturalReferenceNonPeople",
                [],
            ),
            brands=lyrics_analysis.get("brands", []),
            locations=lyrics_analysis.get("locations", []),
            narrative_style=lyrics_analysis.get("narrativeStyle", ""),
            emotional_intensity_score=lyrics_analysis.get("emotionalIntensityScore", 0),
            complexity_score=lyrics_analysis.get("complexityScore", 0),
            repetitiveness_score=lyrics_analysis.get("repetitivenessScore", 0),
            rhyme_scheme_score=lyrics_analysis.get("rhymeSchemeScore", 0),
            imagery_score=lyrics_analysis.get("imageryScore", 0),
        )
        await self._upsert_neo4j_node("LyricsAnalysis", analysis_model.dict())
        await self._upsert_neo4j_relationship(
            track_id,
            analysis_model.id,
            "HAS_LYRICS_ANALYSIS",
        )

    async def _process_isrc(self, isrc_data: Dict, track_id: str) -> None:
        isrc = ISRC(
            id=f"isrc_{isrc_data['value']}",
            value=isrc_data["value"],
            country_code=isrc_data["countryCode"],
            country_name=isrc_data["countryName"],
        )
        await self._upsert_neo4j_node("ISRC", isrc.dict())

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

    async def _create_track_node(self, track_data: Dict) -> str:
        """Create a Track node from track data."""
        soundcharts_track_id = track_data["uuid"]

        track = Track(
            id=str(uuid.uuid4()),  # Always generate new UUID
            name=track_data["name"],
            credit_name=track_data.get("creditName"),
            release_date=track_data.get("releaseDate"),
            copyright=track_data.get("copyright"),
            app_url=track_data.get("appUrl"),
            image_url=track_data.get("imageUrl"),
            duration=track_data.get("duration"),
            explicit=track_data.get("explicit"),
            composers=track_data.get("composers", []),
            producers=track_data.get("producers", []),
            language_code=track_data.get("languageCode"),
            soundcharts_uuid=soundcharts_track_id,
        )
        await self._upsert_neo4j_node("Track", track.dict())
        return track.id

    async def _create_album_node(self, album_data: Dict) -> str:
        """Create an Album node from album data."""
        soundcharts_album_id = album_data["uuid"]

        album = Album(
            id=str(uuid.uuid4()),  # Always generate new UUID
            name=album_data["name"],
            credit_name=album_data.get("creditName"),
            upc=album_data.get("upc"),
            release_date=album_data.get("releaseDate"),
            total_tracks=album_data.get("totalTracks"),
            copyright=album_data.get("copyright"),
            image_url=album_data.get("imageUrl"),
            labels=album_data.get("labels"),
            type=album_data.get("type"),
            soundcharts_uuid=soundcharts_album_id,
        )
        await self._upsert_neo4j_node("Album", album.dict())
        return album.id

    async def _process_related_entities(
        self,
        entity_data: Dict,
        entity_id: str,
    ) -> None:
        """Process related entities for a given entity."""
        # Process artists
        if "artists" in entity_data:
            for artist in entity_data["artists"]:
                try:
                    # Create basic artist node
                    artist_node = {
                        "uuid": artist["uuid"],
                        "soundcharts_uuid": artist["uuid"],
                        "name": artist["name"],
                        "slug": artist.get("slug"),
                        "app_url": artist.get("appUrl"),
                        "image_url": artist.get("imageUrl"),
                    }

                    # Add artist to pending list
                    self._add_to_pending_list("artists", artist["uuid"])

                    # Create artist node
                    await self._upsert_neo4j_node("Artist", artist_node)

                    # Create relationship between entity and artist
                    await self._upsert_neo4j_relationship(
                        entity_id,
                        artist["uuid"],
                        "HAS_ARTIST",
                    )
                except Exception as e:
                    logger.error(
                        "❌ Failed to process artist",
                        artist=artist,
                        error=str(e),
                    )
                    continue

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

        # Process ISRC
        if entity_data.get("isrc", {}).get("value"):
            await self._process_isrc(entity_data["isrc"], entity_id)

        # Process producers and composers
        for role_type in ["producers", "composers"]:
            if role_type in entity_data:
                for name in entity_data[role_type]:
                    artist_model = Artist(id=name, name=name)
                    await self._upsert_neo4j_node("Artist", artist_model.dict())
                    await self._create_role_relationship(
                        entity_id,
                        artist_model.id,
                        role_type[:-1],
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
            await self.neo4j_driver.close()
            logger.info("✅ Neo4j driver closed successfully")
        except Exception as e:
            logger.error("❌ Failed to close Neo4j driver", error=str(e))

    async def _create_artist_node(self, artist_data: Dict) -> str:
        """Create an Artist node from artist data."""
        soundcharts_artist_id = artist_data["uuid"]

        artist = Artist(
            id=str(uuid.uuid4()),
            soundcharts_uuid=soundcharts_artist_id,
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

    def _generate_composite_id(self, prefix: str, *parts: str) -> str:
        """Generate a consistent composite ID from parts."""
        if not parts:
            raise ValueError("At least one part is required for composite ID")

        clean_parts = []
        for part in parts:
            if not part:
                raise ValueError("Empty part in composite ID generation")
            clean_parts.append(str(part).strip().lower().replace(" ", "_"))

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

    async def _create_role_relationship(
        self,
        entity_id: str,
        artist_id: str,
        role: str,
    ) -> None:
        """Create role relationship between entity and artist."""
        await self._upsert_neo4j_relationship(
            entity_id,
            artist_id,
            f"HAS_{role.upper()}",
        )
        await self._upsert_neo4j_node("Role", {"id": f"role_{role}", "name": role})
        await self._upsert_neo4j_relationship(artist_id, f"role_{role}", "HAS_ROLE")

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
            self._add_to_pending_list("artists", artist_data["uuid"])

            # Create artist node
            artist = Artist(
                id=str(uuid.uuid4()),
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
