from typing import List, Optional
from pathlib import Path
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModelSettings
from ..models.task import Task, FileChange, TaskStatus

class CodeChange(BaseModel):
    """Structured code change from AI."""
    file_path: str
    content: str
    diff: Optional[str] = None
    reasoning: str

class CodeResult(BaseModel):
    """Result from code generation."""
    changes: List[CodeChange]
    explanation: str
    confidence: float = 1.0

class CodeAgent:
    """AI code agent using PydanticAI."""
    
    def __init__(self, api_key: str):
        self.agent = Agent(
            "anthropic:claude-3-opus-20240229",
            result_type=CodeResult,
            model_settings=AnthropicModelSettings(
                temperature=0,
                max_tokens=4096,
                anthropic_metadata={"purpose": "code_modification"}
            ),
            system_prompt="""
            You are an expert programmer helping with code changes.
            Analyze the context and task, then provide specific code changes.
            Your response must be structured as CodeResult with:
            - List of CodeChange objects containing file_path and content
            - Clear explanation of changes
            - Confidence score for the changes
            """
        )
        
    @property
    def tools(self):
        """Register tools for the agent."""
        
        @self.agent.tool
        async def read_file(path: str) -> str:
            """Read content of a file."""
            try:
                with open(path) as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {str(e)}"
                
        @self.agent.tool
        async def get_git_diff(path: str) -> str:
            """Get git diff for a file."""
            try:
                import git
                repo = git.Repo(Path.cwd())
                return repo.git.diff(path)
            except Exception as e:
                return f"Error getting diff: {str(e)}"
                
        return [read_file, get_git_diff]

    async def process_task(self, task: Task) -> Task:
        """Process a development task."""
        try:
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            
            # Run agent
            result = await self.agent.run(
                f"""
                Task: {task.title}
                Description: {task.description}
                
                Please analyze the task and suggest code changes.
                Provide specific file modifications with clear explanations.
                """
            )
            
            # Update task with changes
            task.changes = [
                FileChange(
                    path=change.file_path,
                    content=change.content,
                    diff=change.diff
                )
                for change in result.data.changes
            ]
            
            task.status = TaskStatus.COMPLETED
            task.metadata["confidence"] = result.data.confidence
            task.metadata["explanation"] = result.data.explanation
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.metadata["error"] = str(e)
            
        return task 