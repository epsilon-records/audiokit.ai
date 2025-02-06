from typing import List
import re
from pathlib import Path
from ..models.task import Task, TaskStatus

def parse_todo_file(path: Path) -> List[Task]:
    """Parse TODO.txt file into tasks.
    
    Format:
    Priority:
    1. [ ] Task title
       Description: Task description
    """
    tasks = []
    current_priority = 1
    current_task = None
    
    with open(path) as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Check for priority header
            if line.endswith("Priority:"):
                priority_map = {
                    "High": 1,
                    "Medium": 2,
                    "Low": 3
                }
                priority = line.split()[0]
                current_priority = priority_map.get(priority, 3)
                continue
                
            # Check for task
            task_match = re.match(r'\d+\.\s+\[([ xX])\]\s+(.+)$', line)
            if task_match:
                # Save previous task if exists
                if current_task:
                    tasks.append(current_task)
                    
                status = TaskStatus.COMPLETED if task_match.group(1) in 'xX' else TaskStatus.TODO
                title = task_match.group(2)
                
                current_task = Task(
                    title=title,
                    status=status,
                    priority=current_priority
                )
                continue
                
            # Check for description
            if line.startswith("Description:") and current_task:
                current_task.description = line[12:].strip()
                
    # Add final task
    if current_task:
        tasks.append(current_task)
        
    return tasks 