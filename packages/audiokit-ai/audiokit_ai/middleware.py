from fastapi import Request
from packaging import version

async def version_check_middleware(request: Request, call_next):
    client_version = request.headers.get("User-Agent", "").split("/")[-1]
    min_version = "0.1.0"
    
    try:
        if version.parse(client_version) < version.parse(min_version):
            return JSONResponse(
                status_code=426,
                content={"detail": f"Client version {client_version} is outdated"}
            )
    except version.InvalidVersion:
        pass
        
    return await call_next(request) 