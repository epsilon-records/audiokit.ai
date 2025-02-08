"""Tests for Sonic Pi nodes."""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from audiokit_ai.nodes.sources.sonic_pi import SonicPiAINode, MusicalStyle
from audiokit_ai.nodes.sources.sonic_pi_capture import SonicPiCaptureNode


@pytest.fixture
def mock_osc_client():
    """Mock OSC client for testing."""
    with patch("python_osc.OscClient") as mock:
        yield mock


@pytest.fixture
def mock_jack_client():
    """Mock JACK client for testing."""
    with patch("jack.Client") as mock:
        mock_client = Mock()
        mock_client.inports = Mock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_sounddevice():
    """Mock sounddevice for testing."""
    with patch("sounddevice.InputStream") as mock:
        yield mock


class TestSonicPiAINode:
    """Test Sonic Pi AI node functionality."""

    def test_init(self, mock_osc_client):
        """Test node initialization."""
        node = SonicPiAINode("test_node")

        assert node.name == "test_node"
        assert node._style == MusicalStyle.MINIMAL_TECHNO
        assert "complexity" in node.parameters
        assert "mutation_rate" in node.parameters
        assert "filter_cutoff" in node.parameters

    def test_generate_code(self, mock_osc_client):
        """Test code generation."""
        node = SonicPiAINode("test_node")

        with patch("openai.ChatCompletion.create") as mock_openai:
            mock_openai.return_value.choices = [Mock(message=Mock(content="test code"))]

            code = node._generate_code()
            assert isinstance(code, str)
            assert mock_openai.called

    def test_pattern_generation(self, mock_osc_client):
        """Test techno pattern generation."""
        node = SonicPiAINode("test_node")

        pattern = node._generate_techno_pattern(0.5)

        assert "kick" in pattern
        assert "hihat" in pattern
        assert len(pattern["kick"]["pattern"]) == 16  # 4 bars * 4 beats
        assert sum(pattern["kick"]["pattern"]) == 4  # Four-on-the-floor

    def test_execution(self, mock_osc_client):
        """Test code execution via OSC."""
        node = SonicPiAINode("test_node")
        test_code = "use_synth :tb303"

        node._execute_code(test_code)

        mock_osc_client.return_value.send_message.assert_called_with(
            "/run-code", [test_code]
        )


class TestSonicPiCaptureNode:
    """Test Sonic Pi capture node functionality."""

    def test_init_jack(self, mock_jack_client):
        """Test initialization with JACK."""
        node = SonicPiCaptureNode("test_capture", use_jack=True)

        assert node.name == "test_capture"
        assert node._use_jack is True
        assert "input_gain" in node.parameters
        assert mock_jack_client.inports.register.call_count == 2  # Stereo

    def test_init_portaudio(self, mock_sounddevice):
        """Test initialization with PortAudio."""
        node = SonicPiCaptureNode("test_capture", use_jack=False)

        assert node._use_jack is False
        mock_sounddevice.assert_called_once()
        mock_sounddevice.return_value.start.assert_called_once()

    def test_process_audio(self, mock_jack_client):
        """Test audio processing."""
        node = SonicPiCaptureNode("test_capture")

        # Create test buffers
        test_input = np.zeros((2, 1024))
        test_input[0] = np.sin(np.linspace(0, 2 * np.pi, 1024))  # Test sine wave
        node._buffer = test_input

        outputs = [np.zeros(1024), np.zeros(1024)]
        node.process([], outputs)

        # Check if output matches input
        np.testing.assert_array_almost_equal(outputs[0], test_input[0])
        np.testing.assert_array_almost_equal(outputs[1], test_input[1])

    def test_gain_control(self, mock_jack_client):
        """Test input gain parameter."""
        node = SonicPiCaptureNode("test_capture")

        # Set up test buffer
        node._buffer = np.ones((2, 1024)) * 0.5
        node.parameters["input_gain"].value = 2.0

        # Process with gain
        frames = 1024
        node._process_jack(frames)

        # Check if gain was applied
        assert np.all(node._buffer == 1.0)


@pytest.mark.integration
class TestSonicPiIntegration:
    """Integration tests for Sonic Pi nodes."""

    def test_full_chain(self, mock_osc_client, mock_jack_client):
        """Test AI generation and audio capture together."""
        ai_node = SonicPiAINode("test_ai")
        capture_node = SonicPiCaptureNode("test_capture")

        # Generate and execute code
        ai_node.start()
        capture_node.start()

        # Let it run for a bit
        import time

        time.sleep(0.1)

        # Check if audio is being captured
        assert np.any(capture_node._buffer != 0)

        # Cleanup
        ai_node.stop()
        capture_node.stop()


def test_error_handling(mock_osc_client, mock_jack_client):
    """Test error handling in both nodes."""
    ai_node = SonicPiAINode("test_ai")
    capture_node = SonicPiCaptureNode("test_capture")

    # Test OSC connection failure
    mock_osc_client.side_effect = Exception("Connection failed")
    with pytest.raises(Exception):
        ai_node._execute_code("test")

    # Test audio capture failure
    mock_jack_client.activate.side_effect = Exception("JACK failed")
    with pytest.raises(Exception):
        capture_node._setup_audio_client()
