from typing import Dict, List, Set
import numpy as np
import logging
from ..nodes.base import AudioNode

logger = logging.getLogger(__name__)


class AudioGraphManager:
    """Manages the audio processing graph and node connections."""

    def __init__(self, buffer_size: int = 1024):
        self.nodes: Dict[str, AudioNode] = {}
        self.connections: Dict[str, Set[str]] = {}  # source_id -> set of dest_ids
        self._processing_order: List[str] = []
        self._dirty = True
        self.buffer_size = buffer_size
        self.buffers: Dict[str, np.ndarray] = {}

    def add_node(self, node: AudioNode) -> str:
        """Add a node to the graph."""
        self.nodes[node.id] = node
        self.connections[node.id] = set()
        self._dirty = True
        logger.info(f"Added node {node.id} to graph")
        return node.id

    def connect(self, source_id: str, dest_id: str) -> bool:
        """Connect two nodes, return success."""
        if not self._validate_connection(source_id, dest_id):
            return False

        self.connections[source_id].add(dest_id)
        self._dirty = True
        logger.debug(f"Connected {source_id} -> {dest_id}")
        return True

    def disconnect(self, source_id: str, dest_id: str) -> None:
        """Remove a connection between nodes."""
        if dest_id in self.connections[source_id]:
            self.connections[source_id].remove(dest_id)
            self._dirty = True
            logger.debug(f"Disconnected {source_id} -> {dest_id}")

    def _validate_connection(self, source_id: str, dest_id: str) -> bool:
        """Validate a potential connection."""
        if source_id not in self.nodes or dest_id not in self.nodes:
            logger.error(f"Invalid node IDs: {source_id}, {dest_id}")
            return False

        # Check for cycles
        self.connections[source_id].add(dest_id)
        has_cycle = self._detect_cycles()
        self.connections[source_id].remove(dest_id)

        if has_cycle:
            logger.error(f"Connection {source_id} -> {dest_id} would create cycle")
            return False

        return True

    def _detect_cycles(self) -> bool:
        """Return True if graph contains cycles."""
        visited = set()
        path = set()

        def visit(node_id: str) -> bool:
            if node_id in path:
                return True  # Cycle detected
            if node_id in visited:
                return False

            visited.add(node_id)
            path.add(node_id)

            for dest_id in self.connections[node_id]:
                if visit(dest_id):
                    return True

            path.remove(node_id)
            return False

        return any(visit(node_id) for node_id in self.nodes)

    def _update_processing_order(self) -> None:
        """Update topological sort of nodes."""
        if not self._dirty:
            return

        visited = set()
        temp = set()
        order = []

        def visit(node_id: str) -> None:
            if node_id in visited:
                return
            if node_id in temp:
                raise ValueError("Cycle detected during sort")

            temp.add(node_id)

            for dest_id in self.connections[node_id]:
                visit(dest_id)

            temp.remove(node_id)
            visited.add(node_id)
            order.append(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                visit(node_id)

        self._processing_order = order[::-1]
        self._dirty = False
        logger.debug(f"Updated processing order: {self._processing_order}")

    def process(self) -> None:
        """Process one buffer of audio through the graph."""
        if self._dirty:
            self._update_processing_order()

        # Initialize buffers
        self.buffers = {
            node_id: np.zeros(self.buffer_size, dtype=np.float32)
            for node_id in self.nodes
        }

        # Process nodes in topological order
        for node_id in self._processing_order:
            node = self.nodes[node_id]

            # Gather input buffers
            inputs = [
                self.buffers[src_id]
                for src_id, dests in self.connections.items()
                if node_id in dests
            ]

            # Process node
            node.process(inputs, [self.buffers[node_id]])

    def get_buffers(self) -> Dict[str, np.ndarray]:
        """Get the current audio buffers for all nodes."""
        return self.buffers
