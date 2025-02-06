from typing import Dict, List, Optional
from pathlib import Path
import git

class Context:
    """Manages context for AI interactions."""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.repo = git.Repo(root_path)
        self.file_cache = {}
        
    def get_relevant_files(self, task: Task) -> Dict[str, str]:
        """Get files relevant to task."""
        relevant_files = {}
        
        # Get files modified in recent commits
        recent_files = self._get_recent_files()
        
        # Get files mentioned in task
        task_files = self._extract_files_from_task(task)
        
        # Get dependent files based on imports
        dependent_files = self._get_dependent_files(task_files)
        
        # Combine and read files
        all_files = set(recent_files + task_files + dependent_files)
        for file_path in all_files:
            if file_path in self.file_cache:
                content = self.file_cache[file_path]
            else:
                with open(self.root_path / file_path) as f:
                    content = f.read()
                self.file_cache[file_path] = content
            relevant_files[file_path] = content
            
        return relevant_files 