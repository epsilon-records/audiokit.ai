# **AudioKit-AI** 🎶

**AudioKit-AI** is a powerful backend service for audio processing, transcription, and music generation, built with **FastAPI** and powered by state-of-the-art AI models like **Whisper**, **Demucs**, and **DeepFilterNet**.

---

## **Features** ✨

- **Noise Reduction** 🎧 – AI-based denoising for speech and music.
- **Source Separation** 🎤 – Split audio into vocals, drums, bass, and instruments.
- **Speech Transcription** 🗣️ – Accurate speech-to-text using OpenAI's Whisper.
- **Music Generation** 🎹 – Generate music from text prompts (coming soon).
- **Voice Cloning** 🎙️ – Clone voices from short audio samples.
- **MIDI-to-Audio** 🎼 – Convert MIDI files into realistic instrument audio.
- **Genre Classification** 🎸 – Detect music genre and mood from audio.

---

## **Quick Start** 🚀

### **1. Prerequisites**
Ensure you have the following installed:
- **Python 3.11**
- **Docker** (optional, for containerized deployment)

### **2. Install Dependencies**
```bash
pip install hatch
hatch env create
```

### **3. Set Up Environment Variables**
Create a `.env` file in the root directory:
```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET=supersecretkey
JWT_ALGORITHM=HS256
```

### **4. Run the Server**
```bash
hatch run uvicorn audiokit_ai.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:8000/docs` to access the Swagger UI.

---

## **Docker Setup** 🐳

### **1. Build the Docker Image**
```bash
docker build -f docker/Dockerfile -t audiokit_ai .
```

### **2. Run the Container**
```bash
docker run --rm -p 8000:8000 audiokit_ai
```

---

## **API Endpoints** 🌐

| **Endpoint**          | **Method** | **Description**                          |
|------------------------|------------|------------------------------------------|
| `/api/denoise`         | `POST`     | Reduce noise in audio files.             |
| `/api/separate`        | `POST`     | Separate audio into stems (vocals, etc.).|
| `/api/transcribe`      | `POST`     | Transcribe speech to text.              |
| `/api/clone_voice`     | `POST`     | Clone a voice from an audio sample.      |
| `/api/midi_to_audio`   | `POST`     | Convert MIDI to audio.                  |
| `/api/generate_music`  | `POST`     | Generate music from a text prompt.      |

---

## **Tech Stack** 🛠️

- **Backend:** FastAPI, Uvicorn
- **AI Models:** Whisper, Demucs, DeepFilterNet, OpenL3
- **Database:** Redis (rate limiting), FAISS (vector search)
- **Logging:** Loguru (emoji-based logging)
- **Deployment:** Docker, Kubernetes (optional)

---

## **Contributing** 🤝

We welcome contributions! Here's how to get started:

1. **Fork the Repository:**  
   Fork the repository to your GitHub account.

2. **Create a Branch:**  
   Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Commit Your Changes:**  
   Make your changes and commit them with a descriptive message:
   ```bash
   git commit -m "Add your feature or fix"
   ```

4. **Push Your Changes:**  
   Push your changes to your forked repository:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request:**  
   Open a pull request from your branch to the `main` branch of the original repository.

---

## **License** 📜

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## **Acknowledgments** 🙏

- **OpenAI** for Whisper and other open-source models.
- **Facebook AI** for Demucs.
- **DeepFilterNet** for noise reduction.

---

## **Happy Coding!** 🎉
We're excited to have you on board. If you have any questions, feel free to reach out or open an issue in the repository. 