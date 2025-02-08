"""
Microphone Source Node Implementation

Handles real-time audio input from system audio devices using sounddevice.
Provides configurable input settings and automatic device selection.
"""

from typing import Optional, Dict, Any, List
import numpy as np
import sounddevice as sd
from loguru import logger

from audiokit_ai.nodes.source import SourceNode
from audiokit_ai.nodes.base import Parameter


class MicrophoneNode(SourceNode):
    """
    Real-time audio input node using system audio devices.

    Features:
    - Automatic device selection
    - Input level monitoring
    - DC offset removal
    - Configurable sample rate and buffer size
    """

    def __init__(
        self,
        name: str,
        device_id: Optional[int] = None,
        sample_rate: int = 44100,
        buffer_size: int = 1024,
        channels: int = 1,
    ):
        """
        Initialize microphone input node.

        Args:
            name: Human-readable node name
            device_id: Optional specific input device ID
            sample_rate: Input sample rate in Hz
            buffer_size: Audio buffer size in samples
            channels: Number of input channels (1=mono, 2=stereo)
        """
        super().__init__(name)
        logger.info(f"🎤 Creating microphone node: {name}")

        # Store configuration
        self._device_id = device_id
        self._sample_rate = sample_rate
        self._buffer_size = buffer_size
        self._channels = channels

        # Input stream
        self._stream: Optional[sd.InputStream] = None

        # Additional parameters
        self.parameters["input_gain"] = Parameter(
            name="input_gain",
            value=1.0,
            default_value=1.0,
            min_value=0.0,
            max_value=4.0,  # Allow more amplification for weak inputs
            step=0.01,
            automatable=True,
        )
        logger.debug(f"⚙️ Added input gain parameter to {name}")

        self.parameters["dc_offset"] = Parameter(
            name="dc_offset",
            value=0.0,
            default_value=0.0,
            min_value=-1.0,
            max_value=1.0,
            step=0.01,
            automatable=False,
        )
        logger.debug(f"⚙️ Added DC offset parameter to {name}")

        # Input level monitoring
        self._peak_level = 0.0
        self._rms_level = 0.0

        logger.debug(
            f"🔧 Configured microphone node {name} with {channels} channels @ {sample_rate}Hz"
        )

    def _setup_stream(self) -> None:
        """Configure and start the audio input stream."""
        try:
            # Find best matching device if none specified
            if self._device_id is None:
                devices = sd.query_devices()
                logger.debug(f"🔍 Found {len(devices)} audio devices")

                # Filter to input devices with enough channels
                input_devices = [
                    (i, d)
                    for i, d in enumerate(devices)
                    if d["max_input_channels"] >= self._channels
                ]

                if not input_devices:
                    raise RuntimeError("No suitable input devices found")

                # Use first matching device
                self._device_id = input_devices[0][0]
                logger.info(
                    f"📱 Selected input device: {devices[self._device_id]['name']}"
                )

            # Create input stream
            self._stream = sd.InputStream(
                device=self._device_id,
                channels=self._channels,
                samplerate=self._sample_rate,
                blocksize=self._buffer_size,
                callback=self._audio_callback,
            )
            logger.debug("🔌 Created audio input stream")

        except Exception as e:
            logger.error(f"❌ Failed to setup audio input: {str(e)}")
            raise

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: Dict[str, Any],
        status: sd.CallbackFlags,
    ) -> None:
        """Handle incoming audio data from sounddevice."""
        if status:
            logger.warning(f"⚠️ Audio callback status: {str(status)}")

        # Update input buffer
        self._buffer = indata.copy()

        # Update level meters
        self._peak_level = np.max(np.abs(indata))
        self._rms_level = np.sqrt(np.mean(indata**2))

        logger.trace(
            f"📊 Input levels - Peak: {self._peak_level:.2f}, RMS: {self._rms_level:.2f}"
        )

    def start(self, time: Optional[float] = None) -> None:
        """Start audio input capture."""
        if not self._stream:
            self._setup_stream()

        if not self._stream.active:
            logger.info(f"🎤 Starting audio input on {self.name}")
            self._stream.start()
            super().start(time)

    def stop(self, time: Optional[float] = None) -> None:
        """Stop audio input capture."""
        if self._stream and self._stream.active:
            logger.info(f"⏹️ Stopping audio input on {self.name}")
            self._stream.stop()
            super().stop(time)

    def process(self, inputs: List[np.ndarray], outputs: List[np.ndarray]) -> None:
        """
        Process audio from input device.

        Applies:
        - Input gain
        - DC offset correction
        - Basic noise gate
        """
        start_time = np.datetime64("now")

        if not self.state.active or self._buffer is None:
            logger.trace(f"💤 {self.name} inactive or no input - outputting silence")
            for output in outputs:
                output.fill(0)
            return

        # Get parameters
        input_gain = self.get_parameter("input_gain")
        dc_offset = self.get_parameter("dc_offset")

        # Process each output
        for i, output in enumerate(outputs):
            if i < self._buffer.shape[1]:  # Only process available channels
                # Apply DC offset correction and gain
                output[:] = (self._buffer[:, i] - dc_offset) * input_gain

                logger.trace(
                    f"🔊 Processed channel {i} with gain={input_gain:.2f}, "
                    f"DC offset={dc_offset:.2f}"
                )

        # Update metrics
        end_time = np.datetime64("now")
        process_time = (end_time - start_time) / np.timedelta64(1, "ms")

        self.update_metrics(
            cpu_load=process_time / (self._buffer_size / self._sample_rate) * 100,
            latency=process_time + (self._buffer_size / self._sample_rate * 1000),
        )

    def get_levels(self) -> Dict[str, float]:
        """Get current input levels."""
        return {"peak": self._peak_level, "rms": self._rms_level}

    def __del__(self):
        """Cleanup resources."""
        if self._stream:
            self._stream.stop()
            self._stream.close()
            logger.debug(f"🧹 Cleaned up audio stream for {self.name}")
