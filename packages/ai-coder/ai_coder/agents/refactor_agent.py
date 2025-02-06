from typing import List, Dict, Any
from pydantic import BaseModel
from .base import BaseAgent, AgentResult
from pathlib import Path
from .utils import sandbox_required
from .exceptions import SecurityViolation

class Refactoring(BaseModel):
    """Code refactoring change."""
    file_path: str
    content: str
    improvement: str

class RefactorResult(AgentResult):
    """Result from Refactor agent."""
    changes: List[Refactoring]

class RefactorAgent(BaseAgent):
    """Improves and simplifies existing code."""
    
    @property
    def system_prompt(self) -> str:
        return """
        You are an expert in code refactoring and improvement. Your role is to:
        1. Identify code smells and technical debt
        2. Suggest and implement improvements
        3. Maintain functionality while simplifying
        4. Document refactoring rationale
        """
    
    @property
    def result_type(self) -> type:
        return RefactorResult 

    @sandbox_required
    async def process(self, context: Dict[str, Any]) -> RefactorResult:
        try:
            # Read files through sandbox
            changes = []
            for file_path in context.get("files", []):
                content = await self.read_file(Path(file_path))
                # Process refactoring...
            
            # Write refactored files through sandbox
            for change in changes:
                await self.write_file(
                    Path(change.file_path),
                    change.content
                )
                
            return RefactorResult(success=True, changes=changes)
        except SecurityViolation as e:
            return RefactorResult(
                success=False,
                message=f"Security violation: {str(e)}"
            ) 