import os
import tempfile
from typing import Dict, Optional, Tuple

import acoustid
from pydub import AudioSegment
from structlog import get_logger


logger = get_logger()


class AudioService:
    def __init__(self, settings):
        """Initialize AudioService with AcoustID API key."""
        self.settings = settings
        self.acoustid_api_key = settings.acoustid_api_key

    async def process_audio(self, audio_data: bytes, filename: str) -> Tuple[str, Dict]:
        """
        Process audio data to generate fingerprint and extract metadata.

        Args:
            audio_data: Raw audio file data
            filename: Original filename

        Returns:
            Tuple of (fingerprint, metadata)
        """
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(filename)[1],
            ) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name

            try:
                # Generate fingerprint using AcoustID
                duration, fingerprint = acoustid.fingerprint_file(temp_path)

                logger.debug(
                    "AcoustID configuration",
                    api_key=self.acoustid_api_key,
                )

                # Look up metadata using AcoustID
                results = acoustid.lookup(
                    self.acoustid_api_key,
                    fingerprint,
                    duration,
                )
                logger.debug("AcoustID lookup results", results=results)

                if not isinstance(results, dict):
                    # Handle unexpected response format
                    acoustid_results = [
                        {"error": "Unexpected response format", "results": str(results)}
                    ]
                elif "error" in results:
                    # Handle error response from AcoustID
                    acoustid_results = [
                        {"error": results["error"], "status": results.get("status")},
                    ]
                else:
                    # Convert results to a list of serializable dictionaries
                    acoustid_results = [
                        {
                            "score": result.get("score", 0.0),
                            "id": result.get("id", ""),
                            "recordings": [
                                {
                                    "id": recording.get("id", ""),
                                    "title": recording.get("title", ""),
                                    "artist": recording.get("artist", ""),
                                }
                                for recording in result.get("recordings", [])
                            ],
                        }
                        for result in results.get("results", [])
                    ]

                # Extract audio features using pydub
                audio = AudioSegment.from_file(temp_path)

                metadata = {
                    "duration": duration,
                    "acoustid_fingerprint": fingerprint,
                    "sample_rate": audio.frame_rate,
                    "channels": audio.channels,
                    "frame_count": len(audio.get_array_of_samples()),
                    "original_filename": filename,
                    "acoustid_results": acoustid_results,
                }

                logger.info(
                    "Audio processed successfully",
                    filename=filename,
                    duration=duration,
                )

                return fingerprint, metadata

            finally:
                # Clean up temporary file
                os.unlink(temp_path)

        except Exception as e:
            logger.error(
                "Failed to process audio file",
                filename=filename,
                error=str(e),
            )
            raise

    def match_fingerprint(self, fingerprint: str, duration: float) -> Optional[Dict]:
        """
        Match a fingerprint against the AcoustID database.

        Args:
            fingerprint: AcoustID fingerprint string
            duration: Audio duration in seconds

        Returns:
            Dictionary of matching results or None if no match
        """
        try:
            results = acoustid.lookup(self.acoustid_api_key, fingerprint, duration)
            return {"matches": list(results)}
        except Exception as e:
            logger.error(
                "Failed to match fingerprint",
                error=str(e),
            )
            return None
