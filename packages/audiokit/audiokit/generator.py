"""Content generators using LlamaIndex knowledge base"""

from typing import Dict, Optional, List
import httpx

from .knowledge_base import KnowledgeBase
from .logger import Logger
from config import cfg


class OpenRouterClient:
    """Simple client for OpenRouter API"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.base_url = f"{cfg.api.openrouter.base_url}/api/v1"
        self.client = httpx.AsyncClient(
            headers={
                "HTTP-Referer": cfg.api.headers.referer,
                "X-Title": cfg.api.headers.title,
                "Authorization": f"Bearer {cfg.api.openrouter.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=30.0,
        )

    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """Send a chat completion request to OpenRouter"""
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": messages,
                },
            )
            response.raise_for_status()
            result = response.json()

            content = (
                result.get("choices", [{}])[0].get("message", {}).get("content", "")
            )
            if not content:
                raise ValueError("Empty response from OpenRouter API")

            return content

        except httpx.HTTPError as e:
            error_msg = str(e)
            Logger.error(f"OpenRouter API request failed: {error_msg}")

            if "429" in error_msg:
                raise ValueError("Rate limit exceeded - please wait before retrying")
            if "402" in error_msg:
                raise ValueError(
                    "Insufficient credits - please check your OpenRouter balance"
                )
            if "401" in error_msg:
                raise ValueError("Authentication failed - check your API key")

            raise ValueError(f"HTTP error: {error_msg}")

        except Exception as e:
            Logger.error(f"Unexpected error in chat completion: {str(e)}")
            raise ValueError(f"Failed to get completion: {str(e)}")

        finally:
            await self.client.aclose()


class ContentGenerator:
    """Base class for content generators using knowledge base"""

    def __init__(self, artist_id: str, model_name: str):
        self.artist_id = artist_id
        self.model_name = model_name
        self.knowledge_base = KnowledgeBase(artist_id)
        self.client = OpenRouterClient(model_name)

    def _build_system_prompt(self, task_description: str, context: str) -> str:
        """Build system prompt with context"""
        return f"""You are an AI assistant specialized in creating content for music artists.

Task: {task_description}

Use the following context to inform your response:
{context}

Guidelines:
- Focus on accuracy and relevance
- Maintain a professional tone
- Include specific details from the context
- Format appropriately for the content type
"""

    async def generate(
        self,
        task_description: str,
        query: str,
        doc_types: Optional[List[str]] = None,
        top_k: int = 5,
    ) -> str:
        """Generate content using knowledge base context"""
        try:
            # Query knowledge base for relevant context
            kb_response = await self.knowledge_base.query(
                query=query, doc_types=doc_types, top_k=top_k
            )

            # Format context from knowledge base
            context = "\n\n".join(
                [
                    f"Source ({node['metadata']['doc_type']} from {node['metadata']['source']}):\n{node['content']}"
                    for node in kb_response["source_nodes"]
                ]
            )

            # Generate content
            messages = [
                {
                    "role": "system",
                    "content": self._build_system_prompt(task_description, context),
                },
                {
                    "role": "user",
                    "content": "Generate the content based on the provided context.",
                },
            ]

            return await self.client.chat_completion(messages)

        except Exception as e:
            Logger.error(f"Failed to generate content: {str(e)}")
            raise


class EPKGenerator(ContentGenerator):
    """Generates Electronic Press Kits"""

    async def generate_epk(self) -> str:
        """Generate EPK using all available artist information"""
        task_description = """Create a comprehensive Electronic Press Kit (EPK) that effectively promotes the artist. 
Include their background, achievements, press coverage, performance history, and unique selling points."""

        query = """Find key information about the artist including:
- Background and biography
- Recent press coverage and reviews
- Performance history and notable shows
- Social media presence and engagement
- Streaming analytics and achievements"""

        doc_types = [
            "artist_profile",
            "press",
            "performances",
            "social_media",
            "analytics",
        ]

        return await self.generate(task_description, query, doc_types)


class InternalReportGenerator(ContentGenerator):
    """Generates Internal Reports"""

    async def generate_report(self) -> str:
        """Generate internal report with analytics and insights"""
        task_description = """Create a detailed internal report analyzing the artist's performance and potential. 
Include data-driven insights, market analysis, and strategic recommendations."""

        query = """Find relevant information for internal analysis including:
- Performance metrics and analytics
- Market positioning
- Growth trends
- Audience demographics
- Platform-specific performance"""

        doc_types = ["analytics", "social_media", "performances", "press"]

        return await self.generate(task_description, query, doc_types)


class BookingEmailGenerator(ContentGenerator):
    """Generates Booking Emails"""

    async def generate_email(self) -> str:
        """Generate personalized booking email"""
        task_description = """Create a professional and compelling booking email that highlights 
the artist's achievements and appeal to venues and promoters."""

        query = """Find relevant information for booking purposes including:
- Recent performance history
- Press coverage and reviews
- Audience size and engagement
- Notable achievements
- Technical requirements"""

        doc_types = ["artist_profile", "performances", "press", "analytics"]

        return await self.generate(task_description, query, doc_types)
