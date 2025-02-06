from typing import List, Dict, Any
from pydantic import BaseModel
from .base import BaseAgent, AgentResult
from pathlib import Path
from .utils import sandbox_required, SecurityViolation

class DiagramUpdate(BaseModel):
    """Mermaid diagram update."""
    content: str
    reason: str

class MermaidResult(AgentResult):
    """Result from Mermaid agent."""
    diagrams: List[DiagramUpdate]

class MermaidAgent(BaseAgent):
    """Manages architectural diagrams in Mermaid format."""
    
    @property
    def system_prompt(self) -> str:
        return """
        You are an expert in software architecture visualization. Your role is to:
        1. Create and update Mermaid diagrams based on code changes
        2. Maintain system architecture documentation
        3. Suggest diagram improvements for clarity
        4. Keep diagrams in sync with code changes
        """
    
    @property
    def result_type(self) -> type:
        return MermaidResult 

    @sandbox_required
    async def process(self, context: Dict[str, Any]) -> MermaidResult:
        try:
            # Read existing diagrams through sandbox
            diagrams_path = Path("docs/diagrams")
            diagrams = []
            
            if (self.sandbox.root_dir / diagrams_path).exists():
                for file in (self.sandbox.root_dir / diagrams_path).glob("*.mmd"):
                    content = await self.read_file(file)
                    # Process diagram...
            
            # Write updated diagrams through sandbox
            for diagram in diagrams:
                await self.write_file(
                    diagrams_path / f"{diagram.name}.mmd",
                    diagram.content
                )
                
            return MermaidResult(success=True, diagrams=diagrams)
        except SecurityViolation as e:
            return MermaidResult(
                success=False,
                message=f"Security violation: {str(e)}"
            ) 