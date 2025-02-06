from typing import Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModelSettings
from ..security.sandbox import Sandbox, sandbox_required

class AgentResult(BaseModel):
    """Base result model for all agents."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class BaseAgent:
    """Base class for all specialized agents."""
    
    def __init__(self, api_key: str, root_dir: Path):
        self.agent = Agent(
            "anthropic:claude-3-opus-20240229",
            result_type=self.result_type,
            model_settings=AnthropicModelSettings(
                temperature=0,
                max_tokens=4096
            ),
            system_prompt=self.system_prompt
        )
        self.sandbox = Sandbox(root_dir)
        
    @property
    def system_prompt(self) -> str:
        """Must be implemented by subclasses."""
        raise NotImplementedError
        
    @property
    def result_type(self) -> type:
        """Must be implemented by subclasses."""
        raise NotImplementedError

    @sandbox_required
    async def process(self, context: Dict[str, Any]) -> AgentResult:
        """Process a task within sandbox boundaries."""
        raise NotImplementedError
        
    @sandbox_required
    async def write_file(self, path: Path, content: str):
        """Safely write file within sandbox."""
        safe_path = self.sandbox.safe_open(path, 'w')
        safe_path.write_text(content)
        
    @sandbox_required
    async def read_file(self, path: Path) -> str:
        """Safely read file within sandbox."""
        safe_path = self.sandbox.safe_open(path, 'r')
        return safe_path.read_text() 