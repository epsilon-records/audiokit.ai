"""Example usage of Sonic Pi nodes."""

import time
from audiokit_ai.nodes.sources.sonic_pi import SonicPiAINode
from audiokit_ai.nodes.sources.sonic_pi_capture import SonicPiCaptureNode

def main():
    # Create nodes
    ai_node = SonicPiAINode("techno_generator")
    capture_node = SonicPiCaptureNode("audio_capture")
    
    try:
        # Start generation and capture
        ai_node.start()
        capture_node.start()
        
        # Let it run for a while
        print("Running for 30 seconds...")
        for _ in range(30):
            time.sleep(1)
            print(f"Peak level: {capture_node._buffer.max():.2f}")
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        # Cleanup
        ai_node.stop()
        capture_node.stop()

if __name__ == "__main__":
    main() 