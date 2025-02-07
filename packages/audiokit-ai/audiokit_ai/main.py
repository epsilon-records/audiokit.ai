from fastapi import FastAPI
from .middleware.validation import RequestValidator
from .auth import AuthHandler
from audiokit_core.config import load_config

app = FastAPI()

# Initialize config properly
config = load_config()
auth_handler = AuthHandler(config)

# Add middleware
app.add_middleware(RequestValidator, auth_handler=auth_handler)

# Existing routes
app.include_router(...) 