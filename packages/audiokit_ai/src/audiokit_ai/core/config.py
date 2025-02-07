from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AudioKit-AI Server"
    redis_host: str = "localhost"
    redis_port: int = 6379
    jwt_secret: str = "supersecretkey"
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings() 