"""Audio content indexing and retrieval using LlamaIndex."""

from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from loguru import logger
import openl3
import whisper
from llama_index import (
    VectorIndex,
    ServiceContext,
    StorageContext,
)
from llama_index.vector_stores import PineconeVectorStore
import pinecone


# Load environment variables
load_dotenv()


class AudioIndex:
    """Audio content indexing and retrieval using LlamaIndex + Pinecone."""

    def __init__(
        self,
        pinecone_api_key: Optional[str] = None,
        pinecone_env: Optional[str] = None,
        index_name: str = "audio-embeddings",
    ):
        """Initialize the audio indexing system."""
        # Get config from environment
        self.pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")
        if not self.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY not found in environment")

        self.pinecone_env = pinecone_env or os.getenv(
            "PINECONE_ENVIRONMENT", "us-west1-gcp"
        )

        # Initialize Pinecone
        pinecone.init(api_key=self.pinecone_api_key, environment=self.pinecone_env)

        # Create vector store
        vector_store = PineconeVectorStore(pinecone_index=pinecone.Index(index_name))

        # Create storage context
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Initialize index
        self.index = VectorIndex(
            [],
            storage_context=storage_context,
            service_context=ServiceContext.from_defaults(),
        )

        # Initialize audio processors
        self.audio_model = openl3.models.load_audio_embedding_model(
            input_repr="mel256", content_type="music", embedding_size=512
        )
        self.transcriber = whisper.load_model("base")

        logger.info("Initialized AudioIndex with Pinecone backend")

    def add_audio(self, audio_path: str, metadata: Optional[Dict] = None) -> str:
        """Add audio file to the index."""
        try:
            # Get audio embeddings and transcription
            emb, _ = openl3.get_audio_embedding(audio_path, model=self.audio_model)
            text = self.transcriber.transcribe(audio_path)["text"]

            # Create document with metadata
            doc_metadata = {
                "path": audio_path,
                "embedding": emb.mean(axis=0).tolist(),
                **(metadata or {}),
            }

            # Add to index
            self.index.insert(text, metadata=doc_metadata)
            logger.info(f"Indexed audio file: {audio_path}")

            return os.path.basename(audio_path)

        except Exception as e:
            logger.error(f"Failed to index audio: {str(e)}")
            raise

    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar audio content."""
        try:
            # Query the index
            response = self.index.as_query_engine(similarity_top_k=n_results).query(
                query
            )

            # Format results
            results = []
            for node in response.source_nodes:
                results.append(
                    {
                        "id": os.path.basename(node.metadata["path"]),
                        "metadata": node.metadata,
                        "score": node.score,
                        "text": node.text,
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise

    def delete(self, audio_id: str) -> None:
        """Delete an audio entry from the index."""
        try:
            self.index.delete([audio_id])
            logger.info(f"Deleted audio: {audio_id}")
        except Exception as e:
            logger.error(f"Failed to delete audio {audio_id}: {str(e)}")
            raise

    def __del__(self):
        """Cleanup Pinecone resources."""
        pinecone.deinit()
