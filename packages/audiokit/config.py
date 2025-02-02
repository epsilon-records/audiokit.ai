import os
import yaml
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()  # Load environment variables


class Config:
    _instance = None

    def __init__(self):
        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)

        # Load environment variables into the config structure
        self.config["api"]["soundcharts"]["app_id"] = os.getenv("SOUNDCHARTS_APP_ID")
        self.config["api"]["soundcharts"]["api_key"] = os.getenv("SOUNDCHARTS_API_KEY")
        self.config["api"]["openrouter"]["api_key"] = os.getenv("OPENROUTER_API_KEY")
        self.config["api"]["youtube"]["api_key"] = os.getenv("YOUTUBE_API_KEY")

        # Load Pinecone configuration
        self.config["vector_store"]["pinecone"]["api_key"] = os.getenv(
            "PINECONE_API_KEY"
        )
        self.config["vector_store"]["pinecone"]["index_name"] = os.getenv(
            "PINECONE_INDEX_NAME"
        )
        self.config["vector_store"]["pinecone"]["environment"] = os.getenv(
            "PINECONE_ENVIRONMENT"
        )

        # Add database URL from environment
        self.config["database"] = {"url": os.getenv("DATABASE_URL")}

    def __getattr__(self, name):
        if name in self.config:
            value = self.config[name]
            if isinstance(value, dict):
                return ConfigDict(value)  # Wrap nested dicts
            return value
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def get_path(self, path_name, artist_slug=None):
        path_template = self.config["paths"][path_name]
        if artist_slug:
            path_template = path_template.format(artist_slug=artist_slug)
        return Path(path_template)


class ConfigDict:
    """Helper class to allow dot notation access to nested dictionary"""

    def __init__(self, d):
        self._dict = d

    def __getattr__(self, name):
        if name in self._dict:
            value = self._dict[name]
            if isinstance(value, dict):
                return ConfigDict(value)  # Wrap nested dicts
            return value
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )


# Create and export a singleton instance
cfg = Config.get()
