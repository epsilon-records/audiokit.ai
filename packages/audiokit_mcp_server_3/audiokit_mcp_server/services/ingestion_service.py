from llama_index import Document
from llama_index.node_parser import SentenceSplitter
from structlog import get_logger

from ..utils.embedding_utils import pad_embedding


logger = get_logger()


class IngestionService:
    def __init__(self, llama_index_service):
        self.llama_index_service = llama_index_service
        self.node_parser = SentenceSplitter(chunk_size=512)
        logger.info("Ingestion service initialized")

    async def ingest_document(self, text: str, metadata: dict = None) -> list:
        """Ingest a document into the index."""
        try:
            document = Document(text=text, metadata=metadata or {})
            nodes = self.node_parser.get_nodes_from_documents([document])

            # Ensure embeddings are padded before insertion
            for node in nodes:
                if hasattr(node, "embedding"):
                    node.embedding = pad_embedding(node.embedding, target_dim=1024)

            index = self.llama_index_service.get_index()
            index.insert_nodes(nodes)
            logger.info("Document ingested successfully")
            return [node.node_id for node in nodes]
        except Exception as e:
            logger.error("Document ingestion failed", error=str(e))
            raise
