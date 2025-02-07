import httpx

class AudioKitClient:
    def __init__(self, base_url: str, api_key: str = None, jwt_token: str = None):
        self.base_url = base_url
        self.headers = {}
        if jwt_token:
            self.headers["Authorization"] = f"Bearer {jwt_token}"
        elif api_key:
            self.headers["x-api-key"] = api_key

    def denoise(self, file_path: str):
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "audio/wav")}
            response = httpx.post(f"{self.base_url}/api/denoise", headers=self.headers, files=files)
            response.raise_for_status()
            return response.json()

    def separate(self, file_path: str):
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "audio/wav")}
            response = httpx.post(f"{self.base_url}/api/separate", headers=self.headers, files=files)
            response.raise_for_status()
            return response.json()

    def auto_master(self, file_path: str):
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "audio/wav")}
            response = httpx.post(f"{self.base_url}/api/auto_master", headers=self.headers, files=files)
            response.raise_for_status()
            return response.json()

    def transcribe(self, file_path: str):
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "audio/wav")}
            response = httpx.post(f"{self.base_url}/api/transcribe", headers=self.headers, files=files)
            response.raise_for_status()
            return response.json()

    def clone_voice(self, file_path: str):
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "audio/wav")}
            response = httpx.post(f"{self.base_url}/api/clone_voice", headers=self.headers, files=files)
            response.raise_for_status()
            return response.json()

    def midi_to_audio(self, file_path: str):
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "audio/midi")}
            response = httpx.post(f"{self.base_url}/api/midi_to_audio", headers=self.headers, files=files)
            response.raise_for_status()
            return response.json()

    def generate_music(self, file_path: str):
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "audio/wav")}
            response = httpx.post(f"{self.base_url}/api/generate_music", headers=self.headers, files=files)
            response.raise_for_status()
            return response.json()

    def search_by_sound(self, file_path: str):
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "audio/wav")}
            response = httpx.post(f"{self.base_url}/api/search_by_sound", headers=self.headers, files=files)
            response.raise_for_status()
            return response.json()

    def identify_song(self, file_path: str):
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "audio/wav")}
            response = httpx.post(f"{self.base_url}/api/identify_song", headers=self.headers, files=files)
            response.raise_for_status()
            return response.json()

    def detect_genre(self, file_path: str):
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "audio/wav")}
            response = httpx.post(f"{self.base_url}/api/detect_genre", headers=self.headers, files=files)
            response.raise_for_status()
            return response.json() 