from fastapi import FastAPI

from .core.initialization import initialize_pinecone_index
from .mcp.server import create_mcp_server


# Create FastAPI app
app = FastAPI(title="AudioKit MCP Server 2.0", version="2.0")

# Create and setup MCP server
mcp_server = create_mcp_server()
mcp_server.setup(app)


@app.on_event("startup")
async def startup_event():
    initialize_pinecone_index()


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
