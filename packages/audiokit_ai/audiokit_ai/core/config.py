# CONFIDENTIAL AND PROPRIETARY
# 
# Copyright (c) 2025 AudioKit.ai. All rights reserved.
# 
# This software is confidential and proprietary.
# 

# 
# This file is part of the AudioKit AI package.
# 

from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AudioKit-AI Server"
    redis_host: str = "localhost"
    redis_port: int = 6379
    jwt_secret: str = "supersecretkey"
    jwt_algorithm: str = "HS256"

    # DAW integration settings
    daw_socket_path: str = "/tmp/audiokit_daw.sock"
    max_daw_message_size: int = 10 * 1024 * 1024  # 10MB
    daw_timeout: float = 10.0  # seconds
    max_daw_connections: int = 10

    class Config:
        env_file = ".env"

settings = Settings() 