import json
from pathlib import Path
from typing import Dict, List, Union

from llama_index import Document
from llama_index.node_parser import SimpleNodeParser

from audiokit_mcp_server.core.logger import logger
from audiokit_mcp_server.handlers.llama_index_handler import llama_index_handler


class IngestionPipeline:
    """Unified ingestion pipeline for various data types"""

    def __init__(self):
        self.node_parser = SimpleNodeParser.from_defaults(
            chunk_size=1024,
            chunk_overlap=200,
        )
        logger.info("Ingestion pipeline initialized")

    async def ingest_audio_metadata(self, metadata: Dict) -> List[str]:
        """Ingest audio metadata documents"""
        try:
            # Create document with metadata
            document = Document(
                text=json.dumps(metadata),
                metadata={
                    "type": "audio_metadata",
                    "source": metadata.get("source", "unknown"),
                    "timestamp": metadata.get("timestamp", ""),
                },
            )

            # Parse into nodes
            nodes = self.node_parser.get_nodes_from_documents([document])

            # Insert into index
            llama_index_handler.index.insert_nodes(nodes)

            return [node.node_id for node in nodes]
        except Exception as e:
            logger.error(f"Audio metadata ingestion failed: {e!s}")
            raise

    async def ingest_text_documents(self, documents: List[Dict]) -> List[str]:
        """Ingest text documents"""
        try:
            # Create documents with metadata
            docs = [
                Document(
                    text=doc["content"],
                    metadata=doc.get("metadata", {}),
                )
                for doc in documents
            ]

            # Parse into nodes
            nodes = self.node_parser.get_nodes_from_documents(docs)

            # Insert into index
            llama_index_handler.index.insert_nodes(nodes)

            return [node.node_id for node in nodes]
        except Exception as e:
            logger.error(f"Text document ingestion failed: {e!s}")
            raise

    async def ingest_from_file(self, file_path: Union[str, Path]) -> List[str]:
        """Ingest data from file"""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Read and process file based on type
            if path.suffix == ".json":
                with open(path) as f:
                    data = json.load(f)
                    return await self.ingest_audio_metadata(data)
            elif path.suffix == ".txt":
                with open(path) as f:
                    content = f.read()
                    return await self.ingest_text_documents(
                        [
                            {"content": content, "metadata": {"source": str(path)}},
                        ]
                    )
            else:
                raise ValueError(f"Unsupported file type: {path.suffix}")
        except Exception as e:
            logger.error(f"File ingestion failed: {e!s}")
            raise


# Create singleton instance
ingestion_pipeline = IngestionPipeline()
