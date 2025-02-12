import logging
from typing import Optional

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document
from llama_index.vector_stores.pinecone import PineconeVectorStore

from ..core.config import settings


logger = logging.getLogger(__name__)


def run_ingestion_pipeline(
    audio_path: Optional[str],
    text: Optional[str],
    file_path: Optional[str],
) -> dict:
    """
    Run the ingestion pipeline for audio, text, and file data.
    Uses LlamaIndex to ingest data into Pinecone index 'audiokit-brain'.

    Args:
        audio_path (Optional[str]): Path to the audio file.
        text (Optional[str]): Text data.
        file_path (Optional[str]): Path to the document file.

    Returns:
        dict: Aggregated results of the ingestion operations.
    """
    results = {}

    try:
        # Initialize Pinecone vector store with 'audiokit-brain' index
        vector_store = PineconeVectorStore(
            index_name="audiokit-brain",
            environment=settings.pinecone_env,
            api_key=settings.pinecone_api_key,
        )

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex([], storage_context=storage_context)
        node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)

        # Process audio if provided
        if audio_path:
            from ..handlers.ingestion.audio_ingestor import ingest_audio

            audio_docs = ingest_audio(audio_path)
            if audio_docs:
                nodes = node_parser.get_nodes_from_documents(audio_docs)
                index.insert_nodes(nodes)
                results["audio"] = {
                    "status": "success",
                    "nodes_ingested": len(nodes),
                    "file": audio_path,
                }

        # Process text if provided
        if text:
            text_docs = [Document(text=text)]
            nodes = node_parser.get_nodes_from_documents(text_docs)
            index.insert_nodes(nodes)
            results["text"] = {
                "status": "success",
                "nodes_ingested": len(nodes),
                "text_length": len(text),
            }

        # Process file if provided
        if file_path:
            from ..handlers.ingestion.file_ingestor import ingest_file

            file_docs = ingest_file(file_path)
            if file_docs:
                nodes = node_parser.get_nodes_from_documents(file_docs)
                index.insert_nodes(nodes)
                results["file"] = {
                    "status": "success",
                    "nodes_ingested": len(nodes),
                    "file": file_path,
                }

        return results

    except Exception as e:
        logger.error(f"Ingestion failed: {e!s}")
        return {
            "status": "error",
            "message": str(e),
        }
