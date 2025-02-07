from pathlib import Path
from typing import Optional, Literal
import typer
from rich.table import Table
from rich.console import Console
import yaml
import csv
import io
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from audiokit_core.client import AudioKitClient
from audiokit_core.exceptions import AudioKitAPIError, AudioKitAuthError
from audiokit.plugins.base import CLIPlugin, PluginConfig

class AIClientConfig(PluginConfig):
    api_url: str = "https://api.audiokit.ai/v1"
    default_timeout: int = 30

class AIClientPlugin(CLIPlugin):
    @classmethod 
    def config_schema(cls) -> type[PluginConfig]:
        return AIClientConfig

    def register_commands(self, app: typer.Typer):
        ai_app = typer.Typer(help="Interact with AudioKit AI Server")
        
        @ai_app.command()
        def analyze(
            file_path: Path = typer.Argument(..., exists=True, dir_okay=False),
            timeout: int = typer.Option(None, "--timeout"),
            api_key: str = typer.Option(None, "--key", "-k", envvar="AUDIOKIT_API_KEY"),
            output_format: Literal["table", "json", "yaml", "csv"] = "table"
        ):
            """Analyze audio file with AI processing"""
            client = self._create_client(api_key)
            # ... rest of original analyze implementation

        @ai_app.command()
        def batch_analyze(
            paths: list[Path] = typer.Argument(..., exists=True),
            output_format: Literal["json", "yaml", "csv"] = "json",
            concurrency: int = typer.Option(4, "--concurrency", "-c"),
            timeout: int = typer.Option(None, "--timeout"),
            api_key: str = typer.Option(None, "--key", "-k", envvar="AUDIOKIT_API_KEY")
        ):
            """Batch process audio files with AI"""
            client = self._create_client(api_key)
            # ... rest of original batch_analyze implementation

        app.add_typer(ai_app, name="ai", help="AI server interactions")

    def _create_client(self, api_key: Optional[str]) -> AudioKitClient:
        config = self.get_config()
        client = AudioKitClient(base_url=config.api_url)
        client.config.api_key = api_key
        client.config.default_timeout = config.default_timeout
        return client 