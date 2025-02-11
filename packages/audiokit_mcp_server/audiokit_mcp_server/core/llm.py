"""LLM utilities for AudioKit MCP Server."""

import aiohttp
from fastapi import HTTPException

from audiokit_mcp_server.core.config import settings
from audiokit_mcp_server.core.logger import logger


async def call_llm(prompt: str) -> str:
    """Call OpenRouter LLM API."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.OPENROUTER_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://audiokit.ai",
                    "X-Title": "AudioKit MCP Server",
                },
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                },
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"LLM API error: {error_text}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"LLM API error: {error_text}",
                    )

                data = await response.json()
                return data["choices"][0]["message"]["content"]

    except Exception as e:
        logger.error(f"Failed to call LLM: {e!s}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to call LLM: {e!s}",
        )
