def run_processing_pipeline(file_path: str) -> dict:
    """
    Run the processing pipeline for an audio file.
    Processes the audio and extracts its metadata.

    Args:
        file_path (str): Path to the audio file.

    Returns:
        dict: Aggregated results from processing and metadata extraction.
    """
    from ..handlers.processing import audio_processor, metadata_extractor

    processed = audio_processor.process_audio(file_path)
    metadata = metadata_extractor.extract_metadata(file_path)

    return {
        "processed": processed,
        "metadata": metadata,
    }
