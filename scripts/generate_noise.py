import librosa
import numpy as np
import soundfile as sf


# Load a clean audio file (replace 'clean.wav' with your own)
clean_audio, sr = librosa.load("../packages/audiokit/test.wav", sr=44100)

# Generate white noise
noise = np.random.normal(0, 0.05, clean_audio.shape)

# Mix noise with clean audio
noisy_audio = clean_audio + noise

# Normalize to prevent clipping
noisy_audio = noisy_audio / np.max(np.abs(noisy_audio))

# Save as a WAV file
sf.write("noisy.wav", noisy_audio, sr)

print("Noisy WAV file saved as 'noisy.wav'")
