from typing import List, Optional
import asyncio
from pathlib import Path
from ..models.task import Task, TaskStatus
from ..models.config import RunnerConfig
from .context import Context
from .git import GitManager
from .changes import ChangeManager

class Runner:
    """Main AI command runner."""
    
    def __init__(self, config: RunnerConfig):
        self.config = config
        self.context = Context()
        self.git = GitManager()
        self.changes = ChangeManager()
        
    async def process_task(self, task: Task) -> bool:
        """Process a single task.
        
        Args:
            task: Task to process
            
        Returns:
            bool: True if task completed successfully
        """
        try:
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            
            # Get AI suggestions for changes
            changes = await self.get_changes(task)
            
            # Validate changes
            if not await self.changes.validate(changes):
                task.status = TaskStatus.FAILED
                return False
                
            # Apply changes
            if not await self.changes.apply(changes):
                task.status = TaskStatus.FAILED
                return False
                
            # Run tests if configured
            if self.config.run_tests and not await self.run_tests():
                task.status = TaskStatus.FAILED
                return False
                
            # Commit changes
            if self.config.auto_commit:
                await self.git.commit(
                    changes,
                    message=f"AI-CODER: {task.title}"
                )
                
            task.status = TaskStatus.COMPLETED
            return True
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.metadata["error"] = str(e)
            return False
            
    async def run(self, tasks: List[Task]) -> bool:
        """Run all tasks in order.
        
        Args:
            tasks: List of tasks to process
            
        Returns:
            bool: True if all tasks completed successfully
        """
        success = True
        for task in tasks:
            if not await self.process_task(task):
                success = False
                if self.config.fail_fast:
                    break
        return success 