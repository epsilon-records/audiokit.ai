"""Worker queue system for AudioKit AI."""
from typing import Optional, Any, Callable, Awaitable
import asyncio
from datetime import datetime
from enum import Enum
import uuid
from pydantic import BaseModel, Field
from .storage import JobStorage, RedisJobStorage
from .metrics import WorkerMetrics
import psutil

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
    
    def __init__(self, max_workers: int = 4):
        self.queue = asyncio.Queue()
        self.workers = [
            asyncio.create_task(self._parallel_worker())
            for _ in range(max_workers)
        ]

    async def _parallel_worker(self):
        """Worker handling multiple jobs concurrently"""
        while True:
            job, func = await self.queue.get()
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self._process_job(job, func))
            self.queue.task_done()

    async def _process_job(self, job, func):
        """Process individual job with resource limits"""
        try:
            # Set CPU affinity
            psutil.Process().cpu_affinity([len(self.workers) % psutil.cpu_count()])
            
            # Process with timeout
            await asyncio.wait_for(
                func(job),
                timeout=JOB_TIMEOUT
            )
        except Exception as e:
            logger.error(f"Job failed: {str(e)}")
        
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
        """Submit job to queue with persistent storage.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Created job
        """
        job = Job()
        await self.storage.save_job(job)
        
        # Create bound function with args
        bound_func = lambda: func(*args, **kwargs)
        
        # Create and queue job
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
                    # Add maintenance logging
                    self.maintenance_log.append({
                        "timestamp": datetime.utcnow(),
                        "job": job.id,
                        "status": "started"
                    })
                    
                    # Update job status
                    await self.storage.update_job(job.id, {"status": JobStatus.RUNNING})
                    job.started_at = datetime.utcnow()
                    
                    # Execute job
                    job.result = await func()
                    
                    # Mark complete
                    await self.storage.update_job(job.id, {"status": JobStatus.COMPLETE})
                    job.completed_at = datetime.utcnow()
                    job.progress = 100.0
                    
                except Exception as e:
                    # Handle failure
                    await self.storage.update_job(job.id, {
                        "status": JobStatus.FAILED,
                        "error": str(e)
                    })
                    job.completed_at = datetime.utcnow()
                    job.error = f"{type(e).__name__}: {str(e)}"
                    
                    # Critical failure handling
                    if isinstance(e, (MemoryError, SystemError)):
                        self.maintenance_log.append({
                            "timestamp": datetime.utcnow(),
                            "event": "fatal_error",
                            "error": str(e)
                        })
                        await self.stop()
                        raise
                    
                    self.metrics.log_error(e)
                    
                finally:
                    self.queue.task_done()
                    self.jobs[job.id] = job
                    
        except asyncio.CancelledError:
            pass 