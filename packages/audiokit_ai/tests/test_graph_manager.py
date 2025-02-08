import pytest
import numpy as np
from typing import List
from audiokit_ai.graph.manager import AudioGraphManager
from audiokit_ai.nodes.base import AudioNode


class TestNode(AudioNode):
    """Simple test node that applies gain to input."""

    def __init__(self, node_id: str, gain: float = 1.0):
        self.id = node_id
        self.gain = gain

    def process(self, inputs: List[np.ndarray], outputs: List[np.ndarray]) -> None:
        if len(inputs) == 0:
            # Source node - generate sine wave
            t = np.linspace(0, 1, len(outputs[0]))
            outputs[0][:] = np.sin(2 * np.pi * 440 * t) * self.gain
        else:
            # Effect node - apply gain to sum of inputs
            outputs[0][:] = sum(inputs) * self.gain


def test_add_node():
    graph = AudioGraphManager(buffer_size=512)
    node = TestNode("test1", gain=0.5)

    node_id = graph.add_node(node)
    assert node_id == "test1"
    assert node_id in graph.nodes
    assert node_id in graph.connections
    assert len(graph.connections[node_id]) == 0


def test_connect_nodes():
    graph = AudioGraphManager(buffer_size=512)
    source = TestNode("source", gain=0.5)
    effect = TestNode("effect", gain=2.0)

    graph.add_node(source)
    graph.add_node(effect)

    assert graph.connect("source", "effect")
    assert "effect" in graph.connections["source"]


def test_detect_cycles():
    graph = AudioGraphManager(buffer_size=512)
    node1 = TestNode("node1")
    node2 = TestNode("node2")
    node3 = TestNode("node3")

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)

    # Create chain: node1 -> node2 -> node3
    assert graph.connect("node1", "node2")
    assert graph.connect("node2", "node3")

    # Try to create cycle: node3 -> node1
    assert not graph.connect("node3", "node1")


def test_processing_order():
    graph = AudioGraphManager(buffer_size=512)

    # Create nodes
    source = TestNode("source", gain=0.5)
    effect1 = TestNode("effect1", gain=2.0)
    effect2 = TestNode("effect2", gain=0.8)

    # Add nodes
    graph.add_node(source)
    graph.add_node(effect1)
    graph.add_node(effect2)

    # Connect: source -> effect1 -> effect2
    graph.connect("source", "effect1")
    graph.connect("effect1", "effect2")

    # Process graph
    graph.process()

    # Verify processing order
    assert graph._processing_order.index("source") < graph._processing_order.index(
        "effect1"
    )
    assert graph._processing_order.index("effect1") < graph._processing_order.index(
        "effect2"
    )


def test_audio_processing():
    graph = AudioGraphManager(buffer_size=512)

    # Create simple chain: source -> effect
    source = TestNode("source", gain=0.5)  # 0.5 amplitude sine
    effect = TestNode("effect", gain=2.0)  # doubles amplitude

    graph.add_node(source)
    graph.add_node(effect)
    graph.connect("source", "effect")

    # Process audio
    graph.process()

    # Get the actual processed buffers
    buffers = graph.get_buffers()

    # Verify signal flow
    # Source should output 0.5 amplitude sine
    # Effect should output 1.0 amplitude sine (0.5 * 2.0)
    max_amplitude = np.max(np.abs(buffers["effect"]))
    assert 0.95 < max_amplitude < 1.05  # Allow for some floating point error


def test_disconnect():
    graph = AudioGraphManager(buffer_size=512)
    source = TestNode("source")
    effect = TestNode("effect")

    graph.add_node(source)
    graph.add_node(effect)

    # Connect and verify
    graph.connect("source", "effect")
    assert "effect" in graph.connections["source"]

    # Disconnect and verify
    graph.disconnect("source", "effect")
    assert "effect" not in graph.connections["source"]


def test_invalid_connection():
    graph = AudioGraphManager(buffer_size=512)
    node = TestNode("node1")
    graph.add_node(node)

    # Try to connect to non-existent node
    assert not graph.connect("node1", "nonexistent")
    assert not graph.connect("nonexistent", "node1")


@pytest.mark.parametrize("buffer_size", [128, 512, 1024])
def test_different_buffer_sizes(buffer_size):
    graph = AudioGraphManager(buffer_size=buffer_size)
    source = TestNode("source")
    graph.add_node(source)

    graph.process()
    # Just verify it runs without error for different buffer sizes
