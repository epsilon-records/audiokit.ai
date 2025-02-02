"""Basic example of using AudioKit.

This example demonstrates the most basic usage of AudioKit:
1. Creating an AudioKit instance
2. Loading an audio track
3. Playing the track

Run this example with:
    python basic_usage.py
"""

from pathlib import Path
from audiokit import AudioKit


def main():
    # Initialize AudioKit
    client = AudioKit()

    # Get path to example audio file
    # In a real application, this would be your audio file
    audio_file = Path("example.wav")

    try:
        # Load and play a track
        track = client.load_track(audio_file)
        track.play()

    except FileNotFoundError:
        print(f"Error: Audio file not found: {audio_file}")
        print("Please provide a valid audio file path")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
