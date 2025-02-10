# CONFIDENTIAL AND PROPRIETARY
#
# Copyright (c) 2025 AudioKit.ai. All rights reserved.
#
# This software is confidential and proprietary.
#

#
# This file is part of the AudioKit AI package.
#

import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    app_name: str = "AudioKit-AI Server"
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    jwt_secret: str = os.getenv("JWT_SECRET", "supersecretkey")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")

    # DAW integration settings
    daw_socket_path: str = os.getenv("DAW_SOCKET_PATH", "/tmp/audiokit_daw.sock")
    max_daw_message_size: int = int(
        os.getenv("MAX_DAW_MESSAGE_SIZE", 10 * 1024 * 1024),
    )  # 10MB
    daw_timeout: float = float(os.getenv("DAW_TIMEOUT", 10.0))  # seconds
    max_daw_connections: int = int(os.getenv("MAX_DAW_CONNECTIONS", 10))

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
