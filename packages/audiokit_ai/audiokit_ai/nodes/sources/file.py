"""
File Source Node Implementation

Handles audio file playback with support for various formats using soundfile.
Features include seeking, looping, and real-time playback rate adjustment.
"""

from typing import Optional, List
import os
import numpy as np
import soundfile as sf
from loguru import logger

from audiokit_ai.nodes.source import SourceNode
from audiokit_ai.nodes.base import Parameter


class FileSourceNode(SourceNode):
    """
    Audio file playback node.

    Features:
    - Multiple format support (wav, flac, ogg, etc.)
    - Looping control
    - Real-time playback rate adjustment
    - Automatic resampling
    """

    def __init__(
        self,
        name: str,
        filepath: str,
        loop: bool = False,
        preload: bool = True,
        sample_rate: Optional[int] = None,
    ):
        """Initialize file source node."""
        super().__init__(name)
        logger.info(f"📂 Creating file source node: {name}")

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Audio file not found: {filepath}")

        # Store configuration
        self._filepath = filepath
        self._loop = loop
        self._preload = preload
        self._target_sample_rate = sample_rate

        # File info
        self._info = sf.info(filepath)
        logger.debug(
            f"📄 File info: {self._info.channels}ch, "
            f"{self._info.samplerate}Hz, {self._info.format}"
        )

        # Additional parameters
        self.parameters["loop_start"] = Parameter(
            name="loop_start",
            value=0.0,
            default_value=0.0,
            min_value=0.0,
            max_value=self._info.duration,
            step=0.001,
            automatable=True,
        )
        logger.debug(f"⚙️ Added loop start parameter to {name}")

        self.parameters["loop_end"] = Parameter(
            name="loop_end",
            value=self._info.duration,
            default_value=self._info.duration,
            min_value=0.0,
            max_value=self._info.duration,
            step=0.001,
            automatable=True,
        )
        logger.debug(f"⚙️ Added loop end parameter to {name}")

        # Load audio file
        if preload:
            logger.debug(f"💾 Preloading audio file: {filepath}")
            self._audio_data, self._sample_rate = sf.read(
                filepath, dtype="float32", samplerate=sample_rate
            )
            logger.info(
                f"✅ Loaded {len(self._audio_data) / self._sample_rate:.1f}s "
                f"of audio @ {self._sample_rate}Hz"
            )
        else:
            self._audio_file = sf.SoundFile(filepath)
            self._sample_rate = self._audio_file.samplerate
            logger.debug("🔄 File will be streamed during playback")

    def start(self, time: Optional[float] = None) -> None:
        """Start file playback."""
        if not self.state.active:
            logger.info(
                f"▶️ Starting playback of {os.path.basename(self._filepath)}"
                + (f" at {time}s" if time else "")
            )
            super().start(time)

    def stop(self, time: Optional[float] = None) -> None:
        """Stop file playback."""
        if self.state.active:
            logger.info("⏹️ Stopping playback" + (f" at {time}s" if time else ""))
            super().stop(time)

    def seek(self, position: float) -> None:
        """Seek to position in file."""
        super().seek(position)
        if not self._preload:
            self._audio_file.seek(int(position * self._sample_rate))
        logger.debug(f"⏭️ Seeked to {position:.2f}s")

    def process(self, inputs: List[np.ndarray], outputs: List[np.ndarray]) -> None:
        """Process audio from file."""
        start_time = np.datetime64("now")

        if not self.state.active:
            logger.trace(f"💤 {self.name} inactive - outputting silence")
            for output in outputs:
                output.fill(0)
            return

        # Get parameters
        gain = self.get_parameter("gain")
        playback_rate = self.get_parameter("playback_rate")
        loop_start = self.get_parameter("loop_start")
        loop_end = self.get_parameter("loop_end")

        # Process each output
        for i, output in enumerate(outputs):
            if self._preload:
                # Read from preloaded buffer
                start_idx = self._position
                end_idx = start_idx + len(output)

                if end_idx > len(self._audio_data):
                    if self._loop:
                        # Handle wraparound
                        first_part = self._audio_data[start_idx:]
                        second_part = self._audio_data[
                            : end_idx - len(self._audio_data)
                        ]
                        output[:] = np.concatenate([first_part, second_part])
                        self._position = end_idx - len(self._audio_data)
                    else:
                        # Fill remaining with silence
                        output[: len(self._audio_data) - start_idx] = self._audio_data[
                            start_idx:
                        ]
                        output[len(self._audio_data) - start_idx :].fill(0)
                        self.stop()
                else:
                    output[:] = self._audio_data[start_idx:end_idx]
                    self._position = end_idx
            else:
                # Stream from file
                data = self._audio_file.read(len(output))
                if len(data) < len(output):
                    if self._loop:
                        self._audio_file.seek(0)
                        data = np.concatenate(
                            [data, self._audio_file.read(len(output) - len(data))]
                        )
                    else:
                        output[: len(data)] = data
                        output[len(data) :].fill(0)
                        self.stop()
                        return
                output[:] = data

            # Apply gain
            output *= gain

            logger.trace(
                f"🔊 Processed {len(output)} samples "
                f"(pos={self._position/self._sample_rate:.2f}s, gain={gain:.2f})"
            )

        # Update metrics
        end_time = np.datetime64("now")
        process_time = (end_time - start_time) / np.timedelta64(1, "ms")

        self.update_metrics(
            cpu_load=process_time / (len(outputs[0]) / self._sample_rate) * 100,
            latency=process_time,
        )

    def __del__(self):
        """Cleanup resources."""
        if not self._preload and hasattr(self, "_audio_file"):
            self._audio_file.close()
            logger.debug(f"🧹 Closed audio file: {self._filepath}")
