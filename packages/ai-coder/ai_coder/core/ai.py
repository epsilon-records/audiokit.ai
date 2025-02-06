from typing import List, Dict, Optional
import anthropic
from pydantic import BaseModel
from ..models.task import Task, FileChange

class AIResponse(BaseModel):
    """Structured response from AI."""
    changes: List[FileChange]
    reasoning: str
    confidence: float
    warnings: List[str] = []

class AIManager:
    """Manages AI interactions."""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Client(api_key=api_key)
        self.context_window = []
        
    def _build_prompt(self, task: Task, context: Dict[str, str]) -> str:
        """Build prompt for AI with context."""
        prompt = [
            "You are an expert programmer helping with code changes.",
            "Task:", task.title,
            "Description:", task.description or "",
            "\nRelevant files:\n"
        ]
        
        for path, content in context.items():
            prompt.append(f"\n{path}:\n```\n{content}\n```\n")
            
        prompt.append("\nProvide specific code changes in the following format:")
        prompt.append("```language:path/to/file\n<code changes>\n```")
        
        return "\n".join(prompt)
        
    async def get_changes(self, task: Task, context: Dict[str, str]) -> AIResponse:
        """Get suggested changes from AI."""
        prompt = self._build_prompt(task, context)
        
        try:
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4096,
                temperature=0,
                system="You are an expert programmer. Provide specific, actionable code changes.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response into structured changes
            changes = self._parse_changes(response.content)
            
            return AIResponse(
                changes=changes,
                reasoning=response.content,
                confidence=0.9  # TODO: Implement confidence scoring
            )
            
        except Exception as e:
            raise AIError(f"Failed to get AI suggestions: {str(e)}") 