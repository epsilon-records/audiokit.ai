"""Main FastAPI application

This module configures the main FastAPI application with:
- OpenAPI documentation
- CORS middleware
- Security schemes
- Router registration
- Event handlers
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse

from .knowledge import router as knowledge_router
from ..logger import Logger
from config import cfg


def custom_openapi():
    """Generate custom OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AudioKit AI Platform API",
        version="1.0.0",
        description="""
AudioKit AI Platform API provides endpoints for:
- Artist knowledge base management
- Content generation and analysis
- Platform integrations
- Analytics and reporting

For authentication, use JWT tokens in the Authorization header:
```
Authorization: Bearer <token>
```

Rate limits:
- 100 requests per minute for standard endpoints
- 20 requests per minute for AI generation endpoints
- 5 requests per minute for batch operations
""",
        routes=app.routes,
        tags=[
            {
                "name": "brain",
                "description": "Knowledge base operations including queries and document management",
            },
            {
                "name": "platforms",
                "description": "Platform integration endpoints for data collection and analysis",
            },
            {
                "name": "analytics",
                "description": "Analytics and reporting endpoints",
            },
        ],
    )

    # Security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Global security requirement
    openapi_schema["security"] = [{"bearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI(
    title="AudioKit AI Platform API",
    description="API for AudioKit platform services",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
)


# Custom documentation routes
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Serve custom Swagger UI"""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="AudioKit AI Platform API",
        swagger_favicon_url="/static/favicon.ico",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,  # Hide schemas section by default
            "displayRequestDuration": True,  # Show request duration
            "filter": True,  # Enable filtering
            "tryItOutEnabled": True,  # Enable Try it out by default
        },
    )


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_schema():
    """Serve OpenAPI schema"""
    return JSONResponse(custom_openapi())


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.cors.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers
app.include_router(knowledge_router)


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error",
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    Logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "server_error",
            }
        },
    )


@app.on_event("startup")
async def startup():
    """Startup event handler"""
    Logger.info("Starting AudioKit API")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event handler"""
    Logger.info("Shutting down AudioKit API")
