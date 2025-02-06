from typing import List, Dict, Any
from pydantic import BaseModel
from .base import BaseAgent, AgentResult
from pathlib import Path
from .utils import sandbox_required
from .exceptions import SecurityViolation

class CodeChange(BaseModel):
    """Code change for new features."""
    file_path: str
    content: str
    explanation: str

class CodeResult(AgentResult):
    """Result from Code agent."""
    changes: List[CodeChange]

class CodeAgent(BaseAgent):
    """Implements new features and functionality."""
    
    @property
    def system_prompt(self) -> str:
        return """
        You are an expert programmer implementing new features. Your role is to:
        1. Write clean, efficient code for new features
        2. Follow project standards and patterns
        3. Include proper documentation and tests
        4. Consider edge cases and error handling
        """
    
    @property
    def result_type(self) -> type:
        return CodeResult 

    @sandbox_required
    async def process(self, context: Dict[str, Any]) -> CodeResult:
        task = context.get("task")
        changes = []
        
        try:
            # Read relevant files through sandbox
            for file_path in task.get("files", []):
                content = await self.read_file(Path(file_path))
                # Process content...
            
            # Write changes through sandbox
            for change in changes:
                await self.write_file(
                    Path(change.file_path),
                    change.content
                )
                
            return CodeResult(
                success=True,
                message="Changes applied successfully",
                data={"changes": changes}
            )
        except SecurityViolation as e:
            return CodeResult(
                success=False,
                message=f"Security violation: {str(e)}"
            ) 