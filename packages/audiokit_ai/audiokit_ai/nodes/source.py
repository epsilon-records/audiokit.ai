"""
Source Node Implementation

This module implements audio source nodes that generate or input audio data.
Source nodes can be:
- Microphone input
- Audio file playback
- Oscillators
- AI-generated audio

Each source node manages its own audio generation/input and applies basic
parameters like gain and playback rate.
"""

from typing import Optional, List
import numpy as np
from loguru import logger

from audiokit_ai.nodes.base import AudioNode, Parameter


class SourceNode(AudioNode):
    """
    Base class for audio source nodes.

    Handles common source node functionality like:
    - Start/stop control
    - Gain adjustment
    - Playback rate control
    - Basic audio buffering
    """

    def __init__(self, name: str):
        """
        Initialize a new source node.

        Args:
            name: Human-readable name for this node
        """
        # Initialize base audio node
        super().__init__("source", name)

        logger.info(f"🎚️ Initializing source node: {name}")

        # Set up default parameters
        self.parameters["gain"] = Parameter(
            name="gain",
            value=1.0,
            default_value=1.0,
            min_value=0.0,
            max_value=2.0,  # Allow some amplification
            step=0.01,
            automatable=True,
        )
        logger.debug(f"⚙️ Added gain parameter to {name}")

        self.parameters["playback_rate"] = Parameter(
            name="playback_rate",
            value=1.0,
            default_value=1.0,
            min_value=0.25,  # Quarter speed
            max_value=4.0,  # Quadruple speed
            step=0.01,
            automatable=True,
        )
        logger.debug(f"⚙️ Added playback_rate parameter to {name}")

        # Internal state
        self._buffer: Optional[np.ndarray] = None
        self._position: int = 0
        logger.debug(f"🏁 Source node {name} ready")

    def start(self, time: Optional[float] = None) -> None:
        """
        Start audio output from this source.

        Args:
            time: Optional start time in seconds (for scheduled playback)
        """
        if not self.state.active:
            self.state.active = True
            self._position = 0
            logger.info(f"▶️ Started {self.name}" + (f" at {time}s" if time else ""))

    def stop(self, time: Optional[float] = None) -> None:
        """
        Stop audio output from this source.

        Args:
            time: Optional stop time in seconds (for scheduled stops)
        """
        if self.state.active:
            self.state.active = False
            logger.info(f"⏹️ Stopped {self.name}" + (f" at {time}s" if time else ""))

    def seek(self, position: float) -> None:
        """
        Seek to a specific position in the audio.

        Args:
            position: Position in seconds to seek to
        """
        if self._buffer is not None:
            # Convert time to samples
            sample_position = int(position * self._buffer.shape[0])
            self._position = max(0, min(sample_position, self._buffer.shape[0]))
            logger.debug(f"⏭️ Seeked {self.name} to {position:.2f}s")
        else:
            logger.warning(f"⚠️ Cannot seek {self.name} - no buffer available")

    def process(self, inputs: List[np.ndarray], outputs: List[np.ndarray]) -> None:
        """
        Process audio data from this source.

        This base implementation handles:
        - Gain application
        - Playback rate adjustment (basic resampling)
        - Buffer position management

        Args:
            inputs: List of input buffers (usually empty for sources)
            outputs: List of output buffers to fill
        """
        # Skip processing if inactive
        if not self.state.active:
            logger.trace(f"💤 {self.name} inactive - outputting silence")
            for output in outputs:
                output.fill(0)
            return

        # Get current parameter values
        gain = self.get_parameter("gain")
        playback_rate = self.get_parameter("playback_rate")

        start_time = np.datetime64("now")

        # Process each output buffer
        if self._buffer is not None:
            for output in outputs:
                # Calculate how many samples to read based on playback rate
                samples_needed = int(len(output) * playback_rate)

                # Read from buffer with wraparound
                for i in range(len(output)):
                    output[i] = self._buffer[self._position] * gain
                    self._position = (self._position + 1) % len(self._buffer)

                logger.trace(
                    f"🔊 {self.name} processed {len(output)} samples "
                    f"(gain={gain:.2f}, rate={playback_rate:.2f})"
                )
        else:
            # No buffer available - output silence
            logger.warning(f"⚠️ {self.name} has no buffer - outputting silence")
            for output in outputs:
                output.fill(0)

        # Calculate and update metrics
        end_time = np.datetime64("now")
        process_time = (end_time - start_time) / np.timedelta64(1, "ms")

        self.update_metrics(
            cpu_load=process_time / (len(outputs[0]) / 44100) * 100,  # Assuming 44.1kHz
            latency=process_time,
        )
