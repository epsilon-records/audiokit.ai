"""
Oscillator Source Node Implementation

Provides various waveform types with anti-aliasing and modulation capabilities.
Features frequency and phase control for basic synthesis operations.
"""

from typing import List, Literal, Optional
from enum import Enum
import numpy as np
from loguru import logger

from audiokit_ai.nodes.source import SourceNode
from audiokit_ai.nodes.base import Parameter


class WaveformType(str, Enum):
    """Available waveform types."""

    SINE = "sine"
    SQUARE = "square"
    SAW = "saw"
    TRIANGLE = "triangle"
    NOISE = "noise"


class OscillatorNode(SourceNode):
    """
    Oscillator node for generating basic waveforms.

    Features:
    - Multiple waveform types
    - Anti-aliased waveforms
    - Frequency and phase control
    - Optional FM/PM modulation
    """

    def __init__(
        self,
        name: str,
        waveform: WaveformType = WaveformType.SINE,
        frequency: float = 440.0,
        sample_rate: int = 44100,
    ):
        """Initialize oscillator node."""
        super().__init__(name)
        logger.info(f"🎹 Creating oscillator node: {name}")

        # Store configuration
        self._waveform = waveform
        self._sample_rate = sample_rate
        self._phase = 0.0

        # Additional parameters
        self.parameters["frequency"] = Parameter(
            name="frequency",
            value=frequency,
            default_value=440.0,
            min_value=20.0,  # 20Hz minimum (below human hearing)
            max_value=20000.0,  # 20kHz maximum (above human hearing)
            step=0.01,
            automatable=True,
        )
        logger.debug(f"⚙️ Added frequency parameter to {name}")

        self.parameters["fine_tune"] = Parameter(
            name="fine_tune",
            value=0.0,
            default_value=0.0,
            min_value=-100.0,  # Cents
            max_value=100.0,
            step=1.0,
            automatable=True,
        )
        logger.debug(f"⚙️ Added fine tune parameter to {name}")

        self.parameters["phase"] = Parameter(
            name="phase",
            value=0.0,
            default_value=0.0,
            min_value=0.0,
            max_value=360.0,
            step=0.1,
            automatable=True,
        )
        logger.debug(f"⚙️ Added phase parameter to {name}")

        # FM modulation parameters
        self.parameters["fm_amount"] = Parameter(
            name="fm_amount",
            value=0.0,
            default_value=0.0,
            min_value=0.0,
            max_value=1000.0,
            step=0.1,
            automatable=True,
        )
        logger.debug(f"⚙️ Added FM amount parameter to {name}")

        logger.debug(
            f"🎵 Configured {waveform.value} oscillator at {frequency}Hz @ {sample_rate}Hz"
        )

    def _generate_sine(self, num_samples: int, frequency: float) -> np.ndarray:
        """Generate anti-aliased sine wave."""
        t = np.linspace(
            self._phase,
            self._phase + (2 * np.pi * frequency * num_samples / self._sample_rate),
            num_samples,
            endpoint=False,
        )
        return np.sin(t)

    def _generate_square(self, num_samples: int, frequency: float) -> np.ndarray:
        """Generate anti-aliased square wave using Fourier series."""
        output = np.zeros(num_samples)
        t = np.linspace(
            self._phase,
            self._phase + (2 * np.pi * frequency * num_samples / self._sample_rate),
            num_samples,
            endpoint=False,
        )

        # Add odd harmonics with decreasing amplitude
        max_harmonic = min(
            int(self._sample_rate / (2 * frequency)),  # Nyquist limit
            31,  # Practical limit for harmonics
        )
        for harmonic in range(1, max_harmonic, 2):
            amplitude = 1.0 / harmonic
            output += amplitude * np.sin(harmonic * t)

        return output * (4 / np.pi)

    def _generate_saw(self, num_samples: int, frequency: float) -> np.ndarray:
        """Generate anti-aliased sawtooth wave using Fourier series."""
        output = np.zeros(num_samples)
        t = np.linspace(
            self._phase,
            self._phase + (2 * np.pi * frequency * num_samples / self._sample_rate),
            num_samples,
            endpoint=False,
        )

        # Add harmonics with alternating signs
        max_harmonic = min(
            int(self._sample_rate / (2 * frequency)),  # Nyquist limit
            31,  # Practical limit for harmonics
        )
        for harmonic in range(1, max_harmonic):
            amplitude = 1.0 / harmonic
            output += amplitude * np.sin(harmonic * t)

        return output * (2 / np.pi)

    def _generate_triangle(self, num_samples: int, frequency: float) -> np.ndarray:
        """Generate anti-aliased triangle wave using Fourier series."""
        output = np.zeros(num_samples)
        t = np.linspace(
            self._phase,
            self._phase + (2 * np.pi * frequency * num_samples / self._sample_rate),
            num_samples,
            endpoint=False,
        )

        # Add odd harmonics with alternating signs and squared denominators
        max_harmonic = min(
            int(self._sample_rate / (2 * frequency)),  # Nyquist limit
            31,  # Practical limit for harmonics
        )
        for harmonic in range(1, max_harmonic, 2):
            amplitude = (-1) ** ((harmonic - 1) / 2) / (harmonic ** 2)
            output += amplitude * np.sin(harmonic * t)

        return output * (8 / (np.pi ** 2))

    def _apply_fm(self, frequency: float, fm_input: np.ndarray) -> np.ndarray:
        """Apply frequency modulation to the base frequency."""
        # Scale FM input to frequency range
        fm_amount = self.get_parameter("fm_amount")
        return frequency * (1.0 + fm_amount * fm_input)

    def process(self, inputs: List[np.ndarray], outputs: List[np.ndarray]) -> None:
        """Generate waveform samples."""
        start_time = np.datetime64("now")

        if not self.state.active:
            logger.trace(f"💤 {self.name} inactive - outputting silence")
            for output in outputs:
                output.fill(0)
            return

        # Get parameters
        gain = self.get_parameter("gain")
        base_freq = self.get_parameter("frequency")
        fine_tune = self.get_parameter("fine_tune")
        phase = np.radians(self.get_parameter("phase"))
        fm_amount = self.get_parameter("fm_amount")

        # Apply fine tuning
        frequency = base_freq * (2 ** (fine_tune / 1200))  # Convert cents to frequency

        # Apply FM if we have input
        if inputs and fm_amount > 0:
            frequency = self._apply_fm(frequency, inputs[0])
            logger.trace(f"📊 Applied FM modulation (amount={fm_amount:.2f})")

        # Process each output
        for output in outputs:
            # Generate waveform
            if self._waveform == WaveformType.SINE:
                output[:] = self._generate_sine(len(output), frequency)
            elif self._waveform == WaveformType.SQUARE:
                output[:] = self._generate_square(len(output), frequency)
            elif self._waveform == WaveformType.SAW:
                output[:] = self._generate_saw(len(output), frequency)
            elif self._waveform == WaveformType.TRIANGLE:
                output[:] = self._generate_triangle(len(output), frequency)
            elif self._waveform == WaveformType.NOISE:
                output[:] = np.random.uniform(-1, 1, len(output))
            else:
                logger.warning(f"⚠️ Unsupported waveform type: {self._waveform}")
                output.fill(0)

            # Apply gain
            output *= gain

            logger.trace(
                f"🔊 Generated {len(output)} samples of {self._waveform.value} wave "
                f"@ {frequency:.1f}Hz (gain={gain:.2f})"
            )

            # Update phase for next buffer
            self._phase += 2 * np.pi * frequency * len(output) / self._sample_rate
            self._phase %= 2 * np.pi

        # Update metrics
        end_time = np.datetime64("now")
        process_time = (end_time - start_time) / np.timedelta64(1, "ms")

        self.update_metrics(
            cpu_load=process_time / (len(outputs[0]) / self._sample_rate) * 100,
            latency=process_time,
        ) 