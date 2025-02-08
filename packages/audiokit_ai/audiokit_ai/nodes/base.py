# CONFIDENTIAL AND PROPRIETARY
# 
# Copyright (c) 2025 AudioKit.ai. All rights reserved.
# 
# This software is confidential and proprietary.
# 

# 
# This file is part of the AudioKit AI package.
# 

"""Base classes and interfaces for AudioKit AI nodes."""

import uuid
from typing import Dict, List, Optional
import numpy as np
from dataclasses import dataclass
from abc import ABC, abstractmethod
from loguru import logger


@dataclass
class Parameter:
    """Configuration parameter for an audio node."""

    name: str
    value: float
    default_value: float
    min_value: float
    max_value: float
    step: Optional[float] = None
    automatable: bool = True


@dataclass
class NodeState:
    """Current state of an audio node."""

    active: bool = False
    bypassed: bool = False
    error: Optional[str] = None
    cpu_load: float = 0.0
    latency: float = 0.0


class AudioNode(ABC):
    """Base class for all audio processing nodes."""

    def __init__(self, node_type: str, name: str):
        self.id = str(uuid.uuid4())
        self.type = node_type
        self.name = name
        self.inputs: List["AudioNode"] = []
        self.outputs: List["AudioNode"] = []
        self.parameters: Dict[str, Parameter] = {}
        self.state = NodeState()
        logger.debug(f"🎵 Created {node_type} node: {name} ({self.id})")

    def connect(
        self, target_node: "AudioNode", channel: Optional[int] = None, gain: float = 1.0
    ) -> None:
        """Connect this node to another node."""
        if target_node not in self.outputs:
            self.outputs.append(target_node)
            target_node.inputs.append(self)
            logger.debug(f"🔌 Connected {self.name} ➡️ {target_node.name}")

    def disconnect(self, target_node: Optional["AudioNode"] = None) -> None:
        """Disconnect this node from another node or all nodes."""
        if target_node:
            if target_node in self.outputs:
                self.outputs.remove(target_node)
                target_node.inputs.remove(self)
                logger.debug(f"❌ Disconnected {self.name} ➡️ {target_node.name}")
        else:
            for node in self.outputs:
                node.inputs.remove(self)
                logger.debug(f"❌ Disconnected {self.name} ➡️ {node.name}")
            self.outputs.clear()

    @abstractmethod
    def process(self, inputs: List[np.ndarray], outputs: List[np.ndarray]) -> None:
        """Process audio data through this node."""
        pass

    def set_parameter(self, name: str, value: float) -> None:
        """Set a parameter value with bounds checking."""
        if name not in self.parameters:
            raise KeyError(f"Parameter {name} not found")
        param = self.parameters[name]
        param.value = min(max(value, param.min_value), param.max_value)
        logger.debug(f"🎛️ Set {self.name}.{name} = {param.value:.2f}")

    def get_parameter(self, name: str) -> float:
        """Get a parameter's current value."""
        if name not in self.parameters:
            raise KeyError(f"Parameter {name} not found")
        return self.parameters[name].value

    def update_metrics(self, cpu_load: float, latency: float) -> None:
        """Update performance metrics for this node."""
        self.state.cpu_load = cpu_load
        self.state.latency = latency
        logger.debug(
            f"📊 {self.name} metrics - CPU: {cpu_load:.1f}%, Latency: {latency:.1f}ms"
        )
