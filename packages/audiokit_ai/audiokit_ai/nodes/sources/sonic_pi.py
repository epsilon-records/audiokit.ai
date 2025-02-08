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
Sonic Pi AI Source Node Implementation

Generates and executes Sonic Pi code in real-time using AI.
Features live coding generation with contextual awareness and pattern learning.
"""

from typing import List, Optional, Dict
import time
import threading
from enum import Enum
import mido
import numpy as np
from loguru import logger
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.osc_server import ThreadingOSCUDPServer
import openai

from audiokit_ai.nodes.source import SourceNode
from audiokit_ai.nodes.base import Parameter
from audiokit_ai.utils.config import get_settings


class MusicalScale(str, Enum):
    """Available musical scales."""

    MAJOR = "major"
    MINOR = "minor"
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    LOCRIAN = "locrian"
    PENTATONIC = "pentatonic"
    BLUES = "blues"
    CHROMATIC = "chromatic"


class MusicalStyle(str, Enum):
    """Available electronic music styles."""

    MINIMAL_TECHNO = "minimal_techno"
    DEEP_HOUSE = "deep_house"
    DUBS_TECHNO = "dub_techno"
    MICROHOUSE = "microhouse"
    ACID = "acid"
    DETROIT_TECHNO = "detroit_techno"
    BERLIN_TECHNO = "berlin_techno"
    AMBIENT_TECHNO = "ambient_techno"


class SonicPiAINode(SourceNode):
    """
    AI-powered Sonic Pi live coding node.

    Features:
    - Real-time code generation
    - Pattern learning from input
    - Contextual awareness
    - Beat and tempo synchronization
    - Error recovery
    """

    def __init__(
        self,
        name: str,
        port: int = 4557,  # Default Sonic Pi OSC port
        model: str = "gpt-4",
        temperature: float = 0.8,
        sample_rate: int = 44100,
        midi_input: Optional[str] = None,
        midi_clock: bool = True,
    ):
        """Initialize Sonic Pi AI node."""
        super().__init__(name)
        logger.info(f"🎼 Creating Sonic Pi AI node: {name}")

        # Configuration
        self._port = port
        self._model = model
        self._sample_rate = sample_rate
        settings = get_settings()
        openai.api_key = settings.openai_api_key

        # Sonic Pi OSC client
        self._osc_client = SimpleUDPClient("127.0.0.1", port)
        self._osc_server = ThreadingOSCUDPServer(("127.0.0.1", port + 1), None)
        self._osc_server.add_handler("/sonic_pi/audio", self._handle_audio)
        logger.debug(f"🔌 Connected to Sonic Pi on port {port}")

        # MIDI setup
        self._midi_input = None
        self._midi_clock_count = 0
        if midi_input:
            try:
                self._midi_input = mido.open_input(midi_input)
                if midi_clock:
                    self._midi_input.callback = self._handle_midi
                logger.info(f"🎹 Connected to MIDI input: {midi_input}")
            except Exception as e:
                logger.error(f"❌ Failed to open MIDI input: {str(e)}")

        # Musical parameters
        self.parameters.update(
            {
                "complexity": Parameter(
                    name="complexity",
                    value=0.5,
                    default_value=0.5,
                    min_value=0.0,
                    max_value=1.0,
                    step=0.01,
                    automatable=True,
                ),
                "mutation_rate": Parameter(
                    name="mutation_rate",
                    value=0.2,
                    default_value=0.2,
                    min_value=0.0,
                    max_value=1.0,
                    step=0.01,
                    automatable=True,
                ),
                "tempo": Parameter(
                    name="tempo",
                    value=120.0,
                    default_value=120.0,
                    min_value=40.0,
                    max_value=200.0,
                    step=0.1,
                    automatable=True,
                ),
                "swing": Parameter(
                    name="swing",
                    value=0.0,
                    default_value=0.0,
                    min_value=0.0,
                    max_value=1.0,
                    step=0.01,
                    automatable=True,
                ),
                "filter_cutoff": Parameter(
                    name="filter_cutoff",
                    value=100.0,
                    default_value=100.0,
                    min_value=20.0,
                    max_value=20000.0,
                    step=0.1,
                    automatable=True,
                ),
                "resonance": Parameter(
                    name="resonance",
                    value=0.3,
                    default_value=0.3,
                    min_value=0.0,
                    max_value=1.0,
                    step=0.01,
                    automatable=True,
                ),
                "delay_time": Parameter(
                    name="delay_time",
                    value=0.25,  # Quarter note delay
                    default_value=0.25,
                    min_value=0.0,
                    max_value=1.0,
                    step=0.01,
                    automatable=True,
                ),
                "delay_feedback": Parameter(
                    name="delay_feedback",
                    value=0.3,
                    default_value=0.3,
                    min_value=0.0,
                    max_value=0.9,
                    step=0.01,
                    automatable=True,
                ),
                "compression": Parameter(
                    name="compression",
                    value=0.5,
                    default_value=0.5,
                    min_value=0.0,
                    max_value=1.0,
                    step=0.01,
                    automatable=True,
                ),
            }
        )

        # Musical state
        self._key = "C"
        self._scale = MusicalScale.MAJOR
        self._style = MusicalStyle.MINIMAL_TECHNO
        self._pattern_length = 8  # bars
        self._current_bar = 0
        self._audio_buffer = np.zeros((2, sample_rate))  # Stereo buffer

        # Pattern generation state
        self._patterns: Dict[str, List[Dict]] = {
            "melody": [],
            "harmony": [],
            "rhythm": [],
            "bass": [],
        }

        # Enhanced prompt template
        self._base_prompt = """
        Generate Sonic Pi code for a {style} pattern in {key} {scale}.
        
        Focus on electronic music elements:
        - Four-on-the-floor beat patterns
        - Minimal, hypnotic sequences
        - Subtle modulation and evolution
        - Deep, rolling basslines
        - Atmospheric textures
        
        Musical Parameters:
        - Tempo: {tempo} BPM
        - Complexity: {complexity}
        - Swing: {swing}
        - Pattern Length: {pattern_length} bars
        - Filter Cutoff: {filter_cutoff} Hz
        - Resonance: {resonance}
        - Delay: {delay_time}s with {delay_feedback} feedback
        
        Current Patterns:
        {patterns}
        
        Previous Code:
        {previous_code}
        
        Generate code that:
        1. Maintains minimal techno/deep house aesthetics
        2. Uses subtle parameter modulation
        3. Creates hypnotic, evolving patterns
        4. Balances rhythm and space
        5. Incorporates dub-style effects
        """

        logger.debug(f"🧠 Initialized AI with {model} model (temp={temperature:.1f})")

    def _handle_audio(self, address: str, *args) -> None:
        """Handle incoming audio from Sonic Pi."""
        if len(args) >= 2:  # Stereo audio
            left, right = args[0], args[1]
            self._audio_buffer[0] = np.frombuffer(left, dtype=np.float32)
            self._audio_buffer[1] = np.frombuffer(right, dtype=np.float32)
            logger.trace(f"🔊 Received audio: {len(left)} samples")

    def _handle_midi(self, msg: mido.Message) -> None:
        """Handle incoming MIDI messages."""
        if msg.type == "clock":
            self._midi_clock_count += 1
            if self._midi_clock_count >= 24:  # One quarter note
                self._midi_clock_count = 0
                self._update_timing()
        elif msg.type == "note_on":
            self._handle_midi_note(msg)

    def _update_timing(self) -> None:
        """Update musical timing based on MIDI clock."""
        self._current_bar = (self._current_bar + 1) % self._pattern_length
        if self._current_bar == 0:
            self._generate_and_execute()

    def _generate_pattern(self, pattern_type: str) -> Dict:
        """Generate a new musical pattern."""
        complexity = self.get_parameter("complexity")

        if pattern_type == "melody":
            # Generate melodic pattern using scale degrees
            pattern = {
                "notes": self._generate_melody(complexity),
                "rhythm": self._generate_rhythm(complexity),
                "octave": 4 + int(complexity * 2),
            }
        elif pattern_type == "harmony":
            # Generate chord progression
            pattern = {
                "chords": self._generate_chords(complexity),
                "rhythm": self._generate_rhythm(complexity * 0.5),
            }
        elif pattern_type == "rhythm":
            # Generate drum pattern
            pattern = {
                "kicks": self._generate_rhythm(complexity),
                "snares": self._generate_rhythm(complexity),
                "hats": self._generate_rhythm(complexity * 1.5),
            }
        else:  # bass
            pattern = {
                "notes": self._generate_bass(complexity),
                "rhythm": self._generate_rhythm(complexity * 0.75),
            }

        return pattern

    def _generate_techno_pattern(self, complexity: float) -> Dict:
        """Generate a techno-specific pattern."""
        pattern = {
            "kick": {
                "pattern": [1, 0, 0, 0] * 4,  # Four-on-the-floor
                "velocity": [1.0, 0.8, 0.9, 0.85],
            },
            "hihat": {
                "pattern": [0, 0, 1, 0] * 4,  # Offbeat hats
                "velocity": [0.7, 0.6, 0.8, 0.6],
            },
            "perc": {
                "pattern": self._generate_minimal_rhythm(complexity),
                "velocity": [0.6 + np.random.random() * 0.2 for _ in range(16)],
            },
            "bass": {
                "notes": self._generate_minimal_bassline(),
                "pattern": [1, 0, 0, 1, 0, 1, 0, 0] * 2,
            },
        }
        return pattern

    def _generate_minimal_rhythm(self, complexity: float) -> List[int]:
        """Generate minimal techno rhythm pattern."""
        # Start with empty 16-step pattern
        pattern = [0] * 16

        # Add essential beats (more likely on strong beats)
        for i in range(16):
            if i % 4 == 0:  # Strong beats
                if np.random.random() < 0.8:
                    pattern[i] = 1
            elif i % 2 == 0:  # Medium beats
                if np.random.random() < 0.4 * complexity:
                    pattern[i] = 1
            else:  # Weak beats
                if np.random.random() < 0.2 * complexity:
                    pattern[i] = 1

        return pattern

    def _generate_minimal_bassline(self) -> List[int]:
        """Generate minimal techno bassline."""
        # Use pentatonic scale for safety
        scale_degrees = [0, 2, 4, 7, 9]
        pattern_length = 8

        # Generate pattern focusing on root and fifth
        pattern = []
        for _ in range(pattern_length):
            if np.random.random() < 0.6:
                note = scale_degrees[0]  # Root note
            elif np.random.random() < 0.8:
                note = scale_degrees[4]  # Fifth
            else:
                note = np.random.choice(scale_degrees)  # Random scale degree
            pattern.append(note)

        return pattern

    def _generate_code(self) -> str:
        """Generate new Sonic Pi code focusing on electronic music."""
        try:
            # Update patterns with techno-specific elements
            if not self._patterns.get("techno"):
                self._patterns["techno"] = []

            complexity = self.get_parameter("complexity")
            if not self._patterns["techno"] or np.random.random() < self.get_parameter(
                "mutation_rate"
            ):
                self._patterns["techno"].append(
                    self._generate_techno_pattern(complexity)
                )

            # Format prompt with electronic music context
            prompt = self._base_prompt.format(
                style=self._style.value,
                key=self._key,
                scale=self._scale.value,
                tempo=self.get_parameter("tempo"),
                complexity=complexity,
                swing=self.get_parameter("swing"),
                pattern_length=self._pattern_length,
                filter_cutoff=self.get_parameter("filter_cutoff"),
                resonance=self.get_parameter("resonance"),
                delay_time=self.get_parameter("delay_time"),
                delay_feedback=self.get_parameter("delay_feedback"),
                patterns=self._patterns,
                previous_code=self._current_code,
            )

            # Generate code with enhanced musical context
            response = openai.ChatCompletion.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert Sonic Pi musician specializing in "
                            f"{self._style.value} music theory and live coding."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.get_parameter("mutation_rate"),
                max_tokens=750,
            )

            new_code = response.choices[0].message.content.strip()
            logger.info(
                f"🎹 Generated new {self._style.value} pattern in "
                f"{self._key} {self._scale.value}"
            )
            logger.debug(f"📝 New code:\n{new_code}")

            return new_code

        except Exception as e:
            logger.error(f"❌ Code generation failed: {str(e)}")
            return self._current_code

    def _execute_code(self, code: str) -> None:
        """Execute code in Sonic Pi."""
        try:
            # Send code to Sonic Pi via OSC
            self._osc_client.send_message("/run-code", [code])
            logger.debug("▶️ Executed code in Sonic Pi")

            # Update state
            self._current_code = code
            self._context_history.append(
                {
                    "code": code,
                    "timestamp": time.time(),
                    "complexity": self.get_parameter("complexity"),
                }
            )

        except Exception as e:
            logger.error(f"❌ Code execution failed: {str(e)}")

    def _execution_loop(self) -> None:
        """Background thread for code execution."""
        while self._running:
            try:
                # Generate and execute new code periodically
                new_code = self._generate_code()
                self._execute_code(new_code)

                # Wait before next generation
                time.sleep(8.0)  # Default to 8-bar patterns at 120 BPM

            except Exception as e:
                logger.error(f"❌ Execution loop error: {str(e)}")
                time.sleep(1.0)  # Error cooldown

    def start(self, time: Optional[float] = None) -> None:
        """Start AI code generation and execution."""
        if not self.state.active:
            logger.info(f"▶️ Starting Sonic Pi AI generation on {self.name}")
            self._running = True
            self._execution_thread = threading.Thread(
                target=self._execution_loop, daemon=True
            )
            self._execution_thread.start()
            super().start(time)

    def stop(self, time: Optional[float] = None) -> None:
        """Stop AI code generation and execution."""
        if self.state.active:
            logger.info(f"⏹️ Stopping Sonic Pi AI generation on {self.name}")
            self._running = False
            if self._execution_thread:
                self._execution_thread.join(timeout=1.0)
            self._execute_code("stop")  # Stop all sounds
            super().stop(time)

    def process(self, inputs: List[np.ndarray], outputs: List[np.ndarray]) -> None:
        """Process audio from Sonic Pi with direct capture."""
        start_time = np.datetime64("now")

        if not self.state.active:
            logger.trace(f"💤 {self.name} inactive - outputting silence")
            for output in outputs:
                output.fill(0)
            return

        # Copy captured audio to outputs
        for i, output in enumerate(outputs):
            if i < 2:  # Stereo output
                output[:] = self._audio_buffer[i][: len(output)]

        # Update metrics
        end_time = np.datetime64("now")
        process_time = (end_time - start_time) / np.timedelta64(1, "ms")

        self.update_metrics(
            cpu_load=process_time / (len(outputs[0]) / self._sample_rate) * 100,
            latency=process_time,
        )

    def set_musical_parameters(
        self,
        key: Optional[str] = None,
        scale: Optional[MusicalScale] = None,
        style: Optional[MusicalStyle] = None,
        pattern_length: Optional[int] = None,
    ) -> None:
        """Update musical parameters."""
        if key:
            self._key = key
            logger.info(f"🎵 Changed key to {key}")
        if scale:
            self._scale = scale
            logger.info(f"🎼 Changed scale to {scale.value}")
        if style:
            self._style = style
            logger.info(f"🎧 Changed style to {style.value}")
        if pattern_length:
            self._pattern_length = pattern_length
            logger.info(f"📏 Changed pattern length to {pattern_length} bars")

    def __del__(self):
        """Cleanup resources."""
        self.stop()
        logger.debug(f"🧹 Cleaned up Sonic Pi AI node: {self.name}")
