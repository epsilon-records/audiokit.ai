from pathlib import Path
import requests
from typing import Optional, Union
from audiokit_core.exceptions import AudioKitAPIError, AudioKitAuthError, AudioKitValidationError, AudioKitRateLimitError, AudioKitServerError
from .config import ClientConfig
from audiokit_core.models.schemas import AudioAnalysis
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from circuitbreaker import circuit
from json import JSONDecodeError
from audiokit_core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class AudioKitClient:
    def __init__(self, config: Optional[ClientConfig] = None):
        self.config = config or ClientConfig()
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        """Configure HTTP session with default headers and auth"""
        self.session.headers.update({
            "User-Agent": f"AudioKitClient/{self.config.version}",
            "Accept": "application/json",
            # Add client version header for error diagnostics
            "X-Client-Version": self.config.version
        })
        if self.config.api_key:
            self.session.headers["X-API-Key"] = self.config.api_key

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=(
            retry_if_exception_type(AudioKitAPIError) |
            retry_if_exception_type(requests.exceptions.Timeout) |
            retry_if_exception_type(requests.exceptions.ConnectionError)
        ),
        before_sleep=lambda _: logger.debug("Retrying due to transient error...")
    )
    @circuit(
        failure_threshold=5,
        recovery_timeout=30,
        expected_exception=AudioKitAPIError
    )
    def analyze_audio(self, file_path: Path, timeout: int = 30) -> AudioAnalysis:
        """Analyze audio file with enhanced error handling"""
        try:
            with file_path.open('rb') as f:
                response = self.session.post(
                    f"{self.config.base_url}/analyze",
                    files={'file': (file_path.name, f, 'audio/wav')},
                    timeout=timeout
                )
            
            # Handle HTTP errors
            self._handle_http_error(response)
            
            return AudioAnalysis(**response.json())
        
        except (JSONDecodeError, ValidationError) as e:
            raise AudioKitAPIError(f"Invalid response format: {str(e)}")
        except Exception as e:
            raise AudioKitAPIError(f"Analysis failed: {str(e)}")

    def _handle_http_error(self, response: requests.Response):
        """Handle HTTP errors with server error translation"""
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            error_detail = None
            try:
                error_data = response.json()
                error_detail = f"{error_data.get('detail')} (code: {error_data.get('code')})"
            except JSONDecodeError:
                error_detail = response.text[:200]  # Truncate long error bodies
            
            status = response.status_code
            if status == 401:
                raise AudioKitAuthError(f"Authentication failed: {error_detail}")
            elif status == 400:
                raise AudioKitValidationError(f"Invalid request: {error_detail}")
            elif status == 429:
                raise AudioKitRateLimitError(f"Rate limit exceeded: {error_detail}")
            elif 500 <= status < 600:
                raise AudioKitServerError(f"Server error ({status}): {error_detail}")
            else:
                raise AudioKitAPIError(f"HTTP error {status}: {error_detail}")

class AsyncAudioKitClient:
    """Asyncio-compatible client using aiohttp"""
    # Implementation omitted for brevity 

class AudioAnalysisResult:
    """Client-facing analysis results"""
    def __init__(self, raw_data: dict):
        self.duration = raw_data['duration']
        self.features = raw_data['features']
        # Add client-specific post-processing 