from fastapi import FastAPI
from .middleware.validation import RequestValidator
from .auth import AuthHandler
from audiokit_core.config import load_config

app = FastAPI(
    title="AudioKit AI",
    version="0.1.0",
    max_request_size=200 * 1024 * 1024,  # 200MB limit
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Initialize config properly
config = load_config()
auth_handler = AuthHandler(config)

# Add middleware
app.add_middleware(RequestValidator, auth_handler=auth_handler)

# Existing routes
app.include_router(...) 