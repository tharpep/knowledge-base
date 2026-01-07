"""Redis queue infrastructure for async job processing."""

import logging
from typing import Optional
from dataclasses import dataclass

from arq import create_pool
from arq.connections import RedisSettings, ArqRedis
from arq.jobs import Job

logger = logging.getLogger(__name__)


@dataclass
class JobStatus:
    """Status of a queued job."""
    job_id: str
    status: str  # queued, processing, completed, failed
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None


class RedisQueue:
    """Redis queue manager using arq."""
    
    def __init__(self, redis_settings: Optional[RedisSettings] = None):
        """Initialize the queue manager."""
        self.settings = redis_settings or RedisSettings(host='localhost', port=6379)
        self._pool: Optional[ArqRedis] = None
    
    async def get_pool(self) -> ArqRedis:
        """Get or create Redis connection pool."""
        if self._pool is None:
            self._pool = await create_pool(self.settings)
        return self._pool
    
    async def enqueue(self, function_name: str, *args, **kwargs) -> str:
        """Enqueue a job for processing."""
        pool = await self.get_pool()
        job = await pool.enqueue_job(function_name, *args, **kwargs)
        logger.info(f"Enqueued job {job.job_id} for {function_name}")
        return job.job_id
    
    async def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """Get the status of a job."""
        try:
            pool = await self.get_pool()
            job = Job(job_id, pool)
            
            status = await job.status()
            info = await job.info()
            
            if info is None:
                return None
            
            status_name = status.name if hasattr(status, 'name') else str(status)
            status_map = {
                'deferred': 'queued',
                'queued': 'queued', 
                'in_progress': 'processing',
                'complete': 'completed',
                'not_found': 'not_found',
            }
            
            enqueue_time = getattr(info, 'enqueue_time', None)
            
            error_msg = None
            result = getattr(info, 'result', None)
            if result is not None and isinstance(result, Exception):
                error_msg = str(result)
            
            return JobStatus(
                job_id=job_id,
                status=status_map.get(status_name, 'unknown'),
                created_at=enqueue_time.isoformat() if enqueue_time else '',
                completed_at=None,
                error=error_msg
            )
        except Exception as e:
            logger.error(f"Error getting job status for {job_id}: {e}")
            raise
    
    async def close(self):
        """Close the Redis connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None


_queue: Optional[RedisQueue] = None


async def get_redis_queue() -> RedisQueue:
    """Get the global RedisQueue instance."""
    global _queue
    if _queue is None:
        from core.config import get_config
        config = get_config()
        settings = RedisSettings(host=config.redis_host, port=config.redis_port)
        _queue = RedisQueue(redis_settings=settings)
    return _queue
