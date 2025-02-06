from typing import List, Dict, Any
from pydantic import BaseModel
from .base import BaseAgent, AgentResult
from pathlib import Path
from .utils import sandbox_required, SecurityViolation

class TodoTask(BaseModel):
    """Structured task for TODO management."""
    title: str
    description: str
    priority: str
    status: str

class TodoResult(AgentResult):
    """Result from TODO agent."""
    tasks: List[TodoTask]

class TodoAgent(BaseAgent):
    """Manages TODO.txt file structure and organization."""
    
    @property
    def system_prompt(self) -> str:
        return """
        You are a task management expert. Your role is to:
        1. Parse and validate TODO.txt files
        2. Suggest task organization and prioritization
        3. Track task dependencies and progress
        4. Keep task descriptions clear and actionable
        """
    
    @property
    def result_type(self) -> type:
        return TodoResult 

    @sandbox_required
    async def process(self, context: Dict[str, Any]) -> TodoResult:
        try:
            # Read TODO file through sandbox
            todo_file = Path("TODO.txt")
            content = await self.read_file(todo_file)
            
            # Process tasks...
            
            # Write updated tasks through sandbox
            await self.write_file(todo_file, updated_content)
            
            return TodoResult(success=True, tasks=tasks)
        except SecurityViolation as e:
            return TodoResult(
                success=False,
                message=f"Security violation: {str(e)}"
            ) 