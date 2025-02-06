from typing import List, Dict, Any
from pydantic import BaseModel
from .base import BaseAgent, AgentResult
from pathlib import Path
from .sandbox import sandbox_required, SecurityViolation

class RuleUpdate(BaseModel):
    """Rule update or addition."""
    rule: str
    rationale: str
    category: str

class RulesResult(AgentResult):
    """Result from Rules agent."""
    updates: List[RuleUpdate]

class RulesAgent(BaseAgent):
    """Manages development rules and standards."""
    
    @property
    def system_prompt(self) -> str:
        return """
        You are an expert in development standards and best practices. Your role is to:
        1. Maintain consistent coding standards
        2. Update rules based on project evolution
        3. Ensure rule clarity and rationale
        4. Track rule dependencies and impacts
        """
    
    @property
    def result_type(self) -> type:
        return RulesResult 

    @sandbox_required
    async def process(self, context: Dict[str, Any]) -> RulesResult:
        try:
            # Read rules through sandbox
            rules_file = Path("RULES.md")
            current_rules = await self.read_file(rules_file)
            
            # Process rules...
            
            # Write updated rules through sandbox
            await self.write_file(rules_file, updated_rules)
            
            return RulesResult(success=True, updates=updates)
        except SecurityViolation as e:
            return RulesResult(
                success=False,
                message=f"Security violation: {str(e)}"
            ) 