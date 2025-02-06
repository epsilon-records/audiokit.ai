"""Worker queue system for AudioKit AI."""
from typing import Optional, Any, Callable, Awaitable
import asyncio
from datetime import datetime
from enum import Enum
import uuid
from pydantic import BaseModel, Field

class JobStatus(str, Enum):
    """Job status states."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"

class Job(BaseModel):
    """Background job."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: JobStatus = JobStatus.QUEUED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    result: Optional[Any] = None
    error: Optional[str] = None

class WorkerPool:
    """Pool of worker tasks."""
    
    def __init__(self, num_workers: int = 5):
        """Initialize worker pool.
        
        Args:
            num_workers: Number of worker tasks
        """
        self.num_workers = num_workers
        self.queue: asyncio.Queue[tuple[Job, Callable[..., Awaitable]]] = asyncio.Queue()
        self.jobs: dict[str, Job] = {}
        self._workers: list[asyncio.Task] = []
        
    async def start(self):
        """Start worker tasks."""
        for _ in range(self.num_workers):
            worker = asyncio.create_task(self._worker())
            self._workers.append(worker)
            
    async def stop(self):
        """Stop worker tasks."""
        # Cancel all workers
        for worker in self._workers:
            worker.cancel()
            
        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        
    async def submit(
        self,
        func: Callable[..., Awaitable],
        *args,
        **kwargs
    ) -> Job:
        """Submit job to queue.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Created job
        """
        # Create bound function with args
        bound_func = lambda: func(*args, **kwargs)
        
        # Create and queue job
        job = Job()
        self.jobs[job.id] = job
        await self.queue.put((job, bound_func))
        
        return job
        
    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job if found, else None
        """
        return self.jobs.get(job_id)
        
    async def _worker(self):
        """Worker task processing jobs."""
        try:
            while True:
                # Get job from queue
                job, func = await self.queue.get()
                
                try:
                    # Update job status
                    job.status = JobStatus.RUNNING
                    job.started_at = datetime.utcnow()
                    
                    # Execute job
                    job.result = await func()
                    
                    # Mark complete
                    job.status = JobStatus.COMPLETE
                    job.completed_at = datetime.utcnow()
                    job.progress = 100.0
                    
                except Exception as e:
                    # Handle failure
                    job.status = JobStatus.FAILED
                    job.completed_at = datetime.utcnow()
                    job.error = str(e)
                    
                finally:
                    self.queue.task_done()
                    
        except asyncio.CancelledError:
            pass 