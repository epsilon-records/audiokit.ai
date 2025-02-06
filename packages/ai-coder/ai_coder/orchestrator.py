from typing import Dict, List, Optional
from pathlib import Path
from pydantic import BaseModel
from .agents import (
    TodoAgent, MermaidAgent, RulesAgent,
    CodeAgent, RefactorAgent
)

class AgentTask(BaseModel):
    """Task for an agent to process."""
    agent_type: str
    priority: int
    context: Dict[str, str]

class Orchestrator:
    """Coordinates multiple specialized agents."""
    
    def __init__(self, api_key: str, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or Path.cwd()
        # Initialize all agents with sandbox
        self.agents = {
            "todo": TodoAgent(api_key, self.root_dir),
            "mermaid": MermaidAgent(api_key, self.root_dir),
            "rules": RulesAgent(api_key, self.root_dir),
            "code": CodeAgent(api_key, self.root_dir),
            "refactor": RefactorAgent(api_key, self.root_dir)
        }
        self.task_queue: List[AgentTask] = []
        
    async def schedule_task(self, task: AgentTask):
        """Add task to queue with priority."""
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda x: x.priority)
        
    async def process_next(self):
        """Process highest priority task."""
        if not self.task_queue:
            return None
            
        task = self.task_queue.pop(0)
        agent = self.agents[task.agent_type]
        return await agent.process(task.context)
        
    async def run_cycle(self):
        """Run a full cycle of agent processing."""
        # First run TODO agent to get current tasks
        todo_result = await self.agents["todo"].process({})
        
        # Schedule other agents based on TODO results
        for task in todo_result.tasks:
            if "diagram" in task.title.lower():
                await self.schedule_task(AgentTask(
                    agent_type="mermaid",
                    priority=task.priority,
                    context={"task": task.dict()}
                ))
            elif "refactor" in task.title.lower():
                await self.schedule_task(AgentTask(
                    agent_type="refactor",
                    priority=task.priority,
                    context={"task": task.dict()}
                ))
            elif "feature" in task.title.lower():
                await self.schedule_task(AgentTask(
                    agent_type="code",
                    priority=task.priority,
                    context={"task": task.dict()}
                ))
                
        # Process all scheduled tasks
        while self.task_queue:
            result = await self.process_next()
            # Handle result (update files, commit changes, etc.) 