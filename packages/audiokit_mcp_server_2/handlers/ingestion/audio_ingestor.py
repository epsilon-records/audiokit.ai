import logging
from typing import List, Optional

from llama_index.core.schema import Document

from ..services.audio_processor import transcribe_audio
from ..services.metadata_extractor import extract_audio_metadata


logger = logging.getLogger(__name__)


def ingest_audio(audio_path: str) -> Optional[List[Document]]:
    """
    Ingest audio file by transcribing and extracting metadata.

    Args:
        audio_path (str): Path to the audio file

    Returns:
        Optional[List[Document]]: List of documents with transcription and metadata
    """
    try:
        # Transcribe audio
        transcription = transcribe_audio(audio_path)

        # Extract metadata
        metadata = extract_audio_metadata(audio_path)

        # Create document with metadata
        doc = Document(
            text=transcription,
            metadata={
                "type": "audio",
                "source": audio_path,
                **metadata,
            },
        )

        return [doc]

    except Exception as e:
        logger.error(f"Audio ingestion failed for {audio_path}: {e!s}")
        return None
