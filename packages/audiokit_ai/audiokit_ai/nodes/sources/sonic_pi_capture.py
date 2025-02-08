# CONFIDENTIAL AND PROPRIETARY
# 
# Copyright (c) 2025 AudioKit.ai. All rights reserved.
# 
# This software is confidential and proprietary.
# 

# 
# This file is part of the AudioKit AI package.
# 

"""
Sonic Pi Audio Capture Node

Captures audio output from Sonic Pi using JACK or PortAudio.
Provides low-latency audio routing into our node system.
"""

from typing import List, Optional, Dict
import numpy as np
import sounddevice as sd
from loguru import logger
import jack

from audiokit_ai.nodes.source import SourceNode
from audiokit_ai.nodes.base import Parameter


class SonicPiCaptureNode(SourceNode):
    """
    Audio capture node for Sonic Pi output.
    
    Features:
    - JACK audio capture (preferred)
    - PortAudio fallback
    - Automatic port connection
    - Buffer management
    - Level metering
    """

    def __init__(
        self,
        name: str,
        use_jack: bool = True,
        buffer_size: int = 1024,
        sample_rate: int = 44100,
    ):
        """Initialize Sonic Pi capture node."""
        super().__init__(name)
        logger.info(f"🎚️ Creating Sonic Pi capture node: {name}")

        # Configuration
        self._use_jack = use_jack
        self._buffer_size = buffer_size
        self._sample_rate = sample_rate
        
        # Audio client setup
        self._client = None
        self._ports = []
        self._buffer = np.zeros((2, buffer_size))  # Stereo buffer
        
        # Level monitoring
        self.parameters["input_gain"] = Parameter(
            name="input_gain",
            value=1.0,
            default_value=1.0,
            min_value=0.0,
            max_value=2.0,
            step=0.01,
            automatable=True,
        )
        
        self._setup_audio_client()
        logger.debug(f"🎛️ Configured audio capture: {'JACK' if use_jack else 'PortAudio'}")

    def _setup_audio_client(self) -> None:
        """Set up audio capture client."""
        try:
            if self._use_jack:
                # Try JACK first
                self._client = jack.Client("sonic_pi_capture")
                self._ports = [
                    self._client.inports.register(f"input_{i+1}") 
                    for i in range(2)
                ]
                
                # Connect to Sonic Pi outputs
                for i, port in enumerate(self._ports):
                    sonic_pi_port = f"sonic-pi:output_{i+1}"
                    self._client.connect(sonic_pi_port, port)
                
                self._client.set_process_callback(self._process_jack)
                self._client.activate()
                logger.info("🔌 Connected to Sonic Pi via JACK")
                
            else:
                # Fall back to PortAudio
                self._stream = sd.InputStream(
                    channels=2,
                    samplerate=self._sample_rate,
                    blocksize=self._buffer_size,
                    callback=self._process_portaudio,
                )
                self._stream.start()
                logger.info("🔌 Connected to Sonic Pi via PortAudio")
                
        except Exception as e:
            logger.error(f"❌ Audio capture setup failed: {str(e)}")
            raise

    def _process_jack(self, frames: int) -> None:
        """Process audio from JACK."""
        try:
            # Capture audio from JACK ports
            for i, port in enumerate(self._ports):
                self._buffer[i] = np.frombuffer(
                    port.get_buffer()[:frames], dtype=np.float32
                )
            
            # Apply input gain
            gain = self.get_parameter("input_gain")
            self._buffer *= gain
            
            logger.trace(f"🎚️ Captured {frames} frames from JACK")
            
        except Exception as e:
            logger.error(f"❌ JACK processing error: {str(e)}")

    def _process_portaudio(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: Dict,
        status: int,
    ) -> None:
        """Process audio from PortAudio."""
        try:
            # Copy input data to buffer
            self._buffer = indata.T  # Transpose to match our format
            
            # Apply input gain
            gain = self.get_parameter("input_gain")
            self._buffer *= gain
            
            logger.trace(f"🎚️ Captured {frames} frames from PortAudio")
            
        except Exception as e:
            logger.error(f"❌ PortAudio processing error: {str(e)}")

    def process(self, inputs: List[np.ndarray], outputs: List[np.ndarray]) -> None:
        """Process captured audio."""
        start_time = np.datetime64("now")

        if not self.state.active:
            logger.trace(f"💤 {self.name} inactive - outputting silence")
            for output in outputs:
                output.fill(0)
            return

        # Copy captured audio to outputs
        for i, output in enumerate(outputs):
            if i < 2:  # Stereo output
                output[:] = self._buffer[i][:len(output)]

        # Calculate levels for metering
        rms = np.sqrt(np.mean(self._buffer ** 2))
        peak = np.max(np.abs(self._buffer))
        logger.trace(f"📊 Levels - RMS: {rms:.2f}, Peak: {peak:.2f}")

        # Update metrics
        end_time = np.datetime64("now")
        process_time = (end_time - start_time) / np.timedelta64(1, "ms")

        self.update_metrics(
            cpu_load=process_time / (len(outputs[0]) / self._sample_rate) * 100,
            latency=process_time,
        )

    def __del__(self):
        """Cleanup resources."""
        if self._use_jack and self._client:
            self._client.deactivate()
            self._client.close()
        elif not self._use_jack and hasattr(self, '_stream'):
            self._stream.stop()
            self._stream.close()
        logger.debug(f"🧹 Cleaned up audio capture for {self.name}") 