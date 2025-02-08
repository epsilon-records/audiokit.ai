# AudioKit Node API Documentation

## Base Node Interface

```typescript
interface AudioNode {
  id: string;                 // Unique identifier for the node
  type: NodeType;            // Source, Processing, Destination, or Utility
  name: string;              // Human-readable name
  inputs: AudioInput[];      // Array of input connections
  outputs: AudioOutput[];    // Array of output connections
  parameters: Parameter[];   // Configurable parameters
  state: NodeState;         // Current state of the node
  
  // Core Methods
  connect(targetNode: AudioNode, options?: ConnectionOptions): void;
  disconnect(targetNode?: AudioNode): void;
  process(inputs: Float32Array[], outputs: Float32Array[]): void;
  setParameter(name: string, value: number): void;
  getParameter(name: string): number;
}

interface Parameter {
  name: string;              // Parameter identifier
  value: number;             // Current value
  defaultValue: number;      // Default value
  min: number;              // Minimum allowed value
  max: number;              // Maximum allowed value
  step?: number;            // Optional step size for value changes
  automatable: boolean;     // Whether parameter can be automated
}

interface NodeState {
  active: boolean;          // Whether node is processing
  bypassed: boolean;        // Whether node is bypassed
  error?: string;          // Error state if any
  metrics: {               // Performance metrics
    cpuLoad: number;      
    latency: number;
  };
}

type NodeType = 'source' | 'processing' | 'destination' | 'utility';

interface ConnectionOptions {
  channel?: number;         // Specific channel to connect
  gain?: number;            // Connection gain/volume
}
```

## Node Type Specifications

### Source Node

```typescript
interface SourceNode extends AudioNode {
  type: 'source';
  
  // Source-specific methods
  start(time?: number): void;
  stop(time?: number): void;
  seek(position: number): void;
  
  // Source-specific parameters
  parameters: Parameter[] & {
    gain: Parameter;
    playbackRate?: Parameter;
  };
}
```

### Processing Node

```typescript
interface ProcessingNode extends AudioNode {
  type: 'processing';
  
  // Processing-specific methods
  bypass(bypassed: boolean): void;
  reset(): void;
  
  // Processing chain methods
  insertBefore(node: ProcessingNode): void;
  insertAfter(node: ProcessingNode): void;
}
```

### Destination Node

```typescript
interface DestinationNode extends AudioNode {
  type: 'destination';
  
  // Destination-specific methods
  mute(muted: boolean): void;
  
  // Destination-specific parameters
  parameters: Parameter[] & {
    volume: Parameter;
    pan: Parameter;
  };
}
```

### Utility Node

```typescript
interface UtilityNode extends AudioNode {
  type: 'utility';
  
  // Utility-specific methods
  route(sourceChannel: number, destChannel: number): void;
  mix(gains: number[]): void;
  split(channels: number): void;
}
```

## Usage Examples

### Creating an Audio Chain

```typescript
// Create nodes
const mic = new SourceNode('microphone');
const noiseSuppressor = new ProcessingNode('noise-suppressor');
const reverb = new ProcessingNode('reverb');
const speakers = new DestinationNode('speakers');

// Connect chain
mic.connect(noiseSuppressor);
noiseSuppressor.connect(reverb);
reverb.connect(speakers);

// Configure parameters
noiseSuppressor.setParameter('threshold', -50);
reverb.setParameter('roomSize', 0.8);
speakers.setParameter('volume', 0.7);

// Start processing
mic.start();
```

### Parameter Automation

```typescript
// Automate reverb mix over time
reverb.parameters.mix.automate({
  startValue: 0,
  endValue: 1,
  duration: 2000, // ms
  curve: 'linear'
});
```
