import base64
from typing import Dict, List, Tuple

import torch
from fastapi import APIRouter, Body, File, UploadFile
from neo4j import GraphDatabase
from pydantic import BaseModel
from structlog import get_logger
from torch_geometric.data import Data

from .config import Settings
from .services.api_service import APIService
from .services.audio_service import AudioService
from .services.llama_index_service import LlamaIndexService


logger = get_logger()


class QueryRequest(BaseModel):
    """Query request model."""

    query: str


class MCPRouter:
    """MCP Router for handling MCP requests."""

    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        self.settings = Settings()
        self.llama_index_service = LlamaIndexService(self.settings)
        self.audio_service = AudioService(self.settings)
        self.api_service = APIService(self.settings)

    def _setup_routes(self):
        """Setup MCP routes."""
        self.router.post("/process")(self.process)
        self.router.post("/ingest")(self.ingest)
        self.router.post("/ingest/audio")(self.ingest_audio)
        self.router.post("/graph/artist")(self.build_artist_graph)

    async def process(self, query: str = Body(...)) -> dict:
        """Process an MCP request."""
        try:
            # Retrieve the answer and sources from the query
            result = await self.llama_index_service.query(query)

            # Write back the LLM output to the vector store so that future queries can improve.
            # Note: writeback_llm_output is a synchronous function; if needed, you can wrap it in
            # an executor to avoid blocking.
            self.llama_index_service.writeback_llm_output(query, result["answer"])

            return {"status": "success", "response": result}
        except Exception as e:
            logger.error("Failed to process MCP request", error=str(e))
            return {"status": "error", "message": str(e)}

    async def ingest(
        self,
        document: str = Body(...),
        metadata: dict = Body(None),
    ) -> dict:
        """Ingest a document into the vector store."""
        try:
            result = self.llama_index_service.ingest_document(document, metadata)
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error("Document ingestion failed", error=str(e))
            return {"status": "error", "message": str(e)}

    async def ingest_audio(self, file: UploadFile = File(...)) -> dict:
        """
        Ingest an audio file, generate fingerprint, and store in vector database.
        """
        try:
            # Read audio file
            audio_data = await file.read()

            # Process audio and generate fingerprint
            fingerprint, metadata = await self.audio_service.process_audio(
                audio_data,
                file.filename,
            )

            # Ensure metadata is JSON-serializable
            serializable_metadata = {
                "type": "audio",
                "fingerprint": base64.b64encode(fingerprint).decode("utf-8"),
                "duration": metadata["duration"],
                "sample_rate": metadata["sample_rate"],
                "channels": metadata["channels"],
                "frame_count": metadata["frame_count"],
                "original_filename": metadata["original_filename"],
                "acoustid_results": metadata["acoustid_results"],
            }
            logger.debug("AcoustID results", results=metadata["acoustid_results"])
            logger.debug("Serializable metadata", metadata=serializable_metadata)

            # Create document text from metadata
            document = f"""
            Audio File: {file.filename}
            Duration: {metadata["duration"]}
            Fingerprint: {fingerprint}
            Sample Rate: {metadata["sample_rate"]}
            Channels: {metadata["channels"]}
            """

            # Ingest document with audio metadata
            result = self.llama_index_service.ingest_document(
                document=document,
                metadata=serializable_metadata,
            )
            logger.debug("Document ingestion result", result=result)

            return {
                "status": "success",
                "result": result,
                "fingerprint": fingerprint,
                "metadata": serializable_metadata,
            }

        except Exception as e:
            logger.error("Audio ingestion failed", error=str(e))
            return {"status": "error", "message": str(e)}

    async def build_artist_graph(self, artist_name: str = Body(...)) -> dict:
        """
        Build a PyG graph for an artist and save it to Neo4j.
        """
        try:
            # Query external APIs for related entities
            soundcharts_data = await self.api_service.query_soundcharts_api(artist_name)
            genius_data = await self.api_service.query_genius_api(artist_name)
            spotify_data = await self.api_service.query_spotify_api(artist_name)
            musicbrainz_data = await self.api_service.query_musicbrainz_api(artist_name)
            billboard_data = await self.api_service.query_billboard_api(artist_name)
            lastfm_data = await self.api_service.query_lastfm_api(artist_name)

            # Create node mappings
            nodes, node_types = self._create_node_mappings(
                artist_name,
                soundcharts_data,
                genius_data,
                spotify_data,
                musicbrainz_data,
                billboard_data,
                lastfm_data,
            )

            # Create edges (collaborations, productions, label signings)
            edges = self._create_edges(
                artist_name,
                nodes,
                soundcharts_data,
                genius_data,
                spotify_data,
                musicbrainz_data,
                billboard_data,
                lastfm_data,
            )

            # Convert to PyG format
            edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
            x = torch.rand((len(nodes), 5))  # 5 feature dimensions
            graph = Data(x=x, edge_index=edge_index)

            # Save graph to Neo4j
            self._save_graph_to_neo4j(nodes, node_types, edges)

            return {
                "status": "success",
                "graph": {
                    "num_nodes": graph.num_nodes,
                    "num_edges": graph.num_edges,
                    "node_mappings": nodes,
                    "node_types": node_types,
                },
            }
        except Exception as e:
            logger.error("Failed to build artist graph", error=str(e))
            return {"status": "error", "message": str(e)}

    def _save_graph_to_neo4j(
        self,
        nodes: Dict[str, int],
        node_types: Dict[int, str],
        edges: List[Tuple[int, int]],
    ) -> None:
        """
        Save the graph to a Neo4j database.
        """
        driver = GraphDatabase.driver(
            self.settings.neo4j_uri,
            auth=(self.settings.neo4j_user, self.settings.neo4j_password),
        )

        with driver.session() as session:
            # Create nodes
            for name, node_id in nodes.items():
                session.write_transaction(
                    self._create_node_tx,
                    node_id,
                    name,
                    node_types[node_id],
                )

            # Create edges
            for src, dst in edges:
                session.write_transaction(
                    self._create_edge_tx,
                    src,
                    dst,
                )

        driver.close()

    @staticmethod
    def _create_node_tx(tx, node_id: int, name: str, node_type: str) -> None:
        """
        Create a node in Neo4j.
        """
        query = "CREATE (n:Node {id: $node_id, name: $name, type: $node_type}) RETURN n"
        tx.run(query, node_id=node_id, name=name, node_type=node_type)

    @staticmethod
    def _create_edge_tx(tx, src: int, dst: int) -> None:
        """
        Create an edge in Neo4j.
        """
        query = (
            "MATCH (a:Node {id: $src}), (b:Node {id: $dst}) "
            "CREATE (a)-[:RELATED_TO]->(b)"
        )
        tx.run(query, src=src, dst=dst)
