"""
Scheduler service for managing background task execution.
Integrates APScheduler with FastAPI lifespan events.
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.services.scheduler_config import SchedulerConfig
from app.services.job_executor import JobExecutor
from app.services.background_jobs import BackgroundJobService
from app.database import SessionLocal

logger = logging.getLogger(__name__)


@dataclass
class JobExecutionInfo:
    """Information about a job execution."""
    job_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # running, success, failed
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_seconds: Optional[float] = None


class SchedulerService:
    """
    Manages APScheduler lifecycle and job registration.
    
    This service:
    - Initializes AsyncIOScheduler with proper configuration
    - Registers all background jobs with their schedules
    - Manages scheduler lifecycle (start/shutdown)
    - Tracks job execution history
    - Provides status information for monitoring
    
    Requirements: 2.1-2.5, 3.1-3.5, 15.1-15.5
    """
    
    def __init__(self, config: Optional[SchedulerConfig] = None):
        """
        Initialize scheduler service.
        
        Args:
            config: Optional SchedulerConfig instance. If None, loads from environment.
        
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
        """
        self.config = config or SchedulerConfig()
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.job_history: Dict[str, JobExecutionInfo] = {}
        
        logger.info(f"SchedulerService initialized with config: {self.config}")
    
    async def start(self) -> None:
        """
        Initialize and start the scheduler.
        
        Creates AsyncIOScheduler with proper configuration:
        - Timezone set to UTC
        - Job defaults: coalesce=True, max_instances=1
        - Misfire grace time configured
        
        Then registers all background jobs and starts the scheduler.
        
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2
        """
        if not self.config.enabled:
            logger.info("Scheduler is disabled by configuration")
            return
        
        try:
            logger.info("Starting scheduler service...")
            
            # Initialize AsyncIOScheduler with configuration (Requirements 2.1, 2.2, 2.3, 2.4, 2.5)
            self.scheduler = AsyncIOScheduler(
                timezone=self.config.timezone,
                job_defaults={
                    'coalesce': True,  # Skip missed runs
                    'max_instances': 1,  # Prevent concurrent execution
                    'misfire_grace_time': self.config.misfire_grace_time
                }
            )
            
            # Register all background jobs (Requirement 3.2)
            self.register_jobs()
            
            # Start the scheduler (Requirement 3.2)
            self.scheduler.start()
            
            logger.info("Scheduler service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}", exc_info=True)
            raise
    
    async def shutdown(self, timeout: Optional[int] = None) -> None:
        """
        Gracefully shutdown scheduler.
        
        Stops accepting new job executions and waits for running jobs to complete
        with a timeout. If jobs exceed timeout, forces shutdown.
        
        Args:
            timeout: Max seconds to wait for jobs to complete. Uses config default if None.
        
        Requirements: 3.3, 3.4, 15.1, 15.2, 15.3, 15.4, 15.5
        """
        if not self.scheduler:
            logger.info("Scheduler not running, nothing to shutdown")
            return
        
        timeout = timeout or self.config.shutdown_timeout
        
        try:
            logger.info(f"Shutting down scheduler (timeout: {timeout}s)...")
            
            # Shutdown scheduler with wait for running jobs (Requirements 15.1, 15.2, 15.3)
            self.scheduler.shutdown(wait=True)
            
            logger.info("Scheduler shutdown completed successfully")
            
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {str(e)}", exc_info=True)
            # Don't re-raise - allow graceful application shutdown
    
    def register_jobs(self) -> None:
        """
        Register all background jobs with their schedules.
        
        Registers 6 background jobs:
        1. check_insurance_expiry - Daily at 00:00 UTC (cron)
        2. check_route_deviations - Every 30 seconds (interval)
        3. reset_daily_cancellation_counts - Daily at 00:00 UTC (cron)
        4. unsuspend_drivers_after_24_hours - Every hour (interval)
        5. reset_daily_availability_hours - Daily at 00:00 UTC (cron)
        6. process_scheduled_rides - Every minute (interval)
        
        Each job is wrapped with JobExecutor for error handling and session management.
        
        Requirements: 4.1-4.4, 5.1-5.4, 6.1-6.4, 7.1-7.4, 8.1-8.4, 9.1-9.4
        """
        if not self.scheduler:
            raise RuntimeError("Scheduler not initialized. Call start() first.")
        
        logger.info("Registering background jobs...")
        
        # Job 1: Check insurance expiry - Daily at 00:00 UTC (Requirements 4.1-4.4)
        self.scheduler.add_job(
            func=self._wrap_job("check_insurance_expiry", self._check_insurance_expiry),
            trigger=CronTrigger(hour=0, minute=0, timezone=self.config.timezone),
            id="check_insurance_expiry",
            name="Check Insurance Expiry",
            replace_existing=True
        )
        logger.info("Registered job: check_insurance_expiry (daily at 00:00 UTC)")
        
        # Job 2: Check route deviations - Every 30 seconds (Requirements 5.1-5.4)
        self.scheduler.add_job(
            func=self._wrap_job("check_route_deviations", self._check_route_deviations),
            trigger=IntervalTrigger(seconds=30),
            id="check_route_deviations",
            name="Check Route Deviations",
            replace_existing=True
        )
        logger.info("Registered job: check_route_deviations (every 30 seconds)")
        
        # Job 3: Reset daily cancellation counts - Daily at 00:00 UTC (Requirements 6.1-6.4)
        self.scheduler.add_job(
            func=self._wrap_job("reset_daily_cancellation_counts", self._reset_daily_cancellation_counts),
            trigger=CronTrigger(hour=0, minute=0, timezone=self.config.timezone),
            id="reset_daily_cancellation_counts",
            name="Reset Daily Cancellation Counts",
            replace_existing=True
        )
        logger.info("Registered job: reset_daily_cancellation_counts (daily at 00:00 UTC)")
        
        # Job 4: Unsuspend drivers after 24 hours - Every hour (Requirements 7.1-7.4)
        self.scheduler.add_job(
            func=self._wrap_job("unsuspend_drivers_after_24_hours", self._unsuspend_drivers_after_24_hours),
            trigger=IntervalTrigger(hours=1),
            id="unsuspend_drivers_after_24_hours",
            name="Unsuspend Drivers After 24 Hours",
            replace_existing=True
        )
        logger.info("Registered job: unsuspend_drivers_after_24_hours (every hour)")
        
        # Job 5: Reset daily availability hours - Daily at 00:00 UTC (Requirements 8.1-8.4)
        self.scheduler.add_job(
            func=self._wrap_job("reset_daily_availability_hours", self._reset_daily_availability_hours),
            trigger=CronTrigger(hour=0, minute=0, timezone=self.config.timezone),
            id="reset_daily_availability_hours",
            name="Reset Daily Availability Hours",
            replace_existing=True
        )
        logger.info("Registered job: reset_daily_availability_hours (daily at 00:00 UTC)")
        
        # Job 6: Process scheduled rides - Every minute (Requirements 9.1-9.4)
        self.scheduler.add_job(
            func=self._wrap_job("process_scheduled_rides", self._process_scheduled_rides),
            trigger=IntervalTrigger(minutes=1),
            id="process_scheduled_rides",
            name="Process Scheduled Rides",
            replace_existing=True
        )
        logger.info("Registered job: process_scheduled_rides (every minute)")
        
        logger.info("All background jobs registered successfully")
    
    def _wrap_job(self, job_name: str, job_method):
        """
        Wrap a job method with JobExecutor for error handling and session management.
        
        Args:
            job_name: Name of the job for logging
            job_method: The method to execute
        
        Returns:
            Wrapped function that can be scheduled
        """
        def wrapped():
            return JobExecutor.execute_job(job_name, job_method)
        return wrapped
    
    def _check_insurance_expiry(self, session) -> List[str]:
        """Execute check_insurance_expiry job."""
        service = BackgroundJobService(session)
        return service.check_insurance_expiry()
    
    def _check_route_deviations(self, session) -> List[dict]:
        """Execute check_route_deviations job."""
        service = BackgroundJobService(session)
        return service.check_route_deviations()
    
    def _reset_daily_cancellation_counts(self, session) -> int:
        """Execute reset_daily_cancellation_counts job."""
        service = BackgroundJobService(session)
        return service.reset_daily_cancellation_counts()
    
    def _unsuspend_drivers_after_24_hours(self, session) -> List[str]:
        """Execute unsuspend_drivers_after_24_hours job."""
        service = BackgroundJobService(session)
        return service.unsuspend_drivers_after_24_hours()
    
    def _reset_daily_availability_hours(self, session) -> int:
        """Execute reset_daily_availability_hours job."""
        service = BackgroundJobService(session)
        return service.reset_daily_availability_hours()
    
    def _process_scheduled_rides(self, session) -> dict:
        """Execute process_scheduled_rides job."""
        service = BackgroundJobService(session)
        return service.process_scheduled_rides()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get scheduler status and job information.
        
        Returns:
            Dictionary containing:
            - running: Whether scheduler is running
            - jobs: List of registered jobs with details
            - total_executions: Total number of job executions
            - failed_executions: Number of failed executions
        
        Requirements: 12.1, 12.2, 12.3, 12.4
        """
        if not self.scheduler:
            return {
                "running": False,
                "jobs": [],
                "total_executions": 0,
                "failed_executions": 0
            }
        
        jobs_info = []
        for job in self.scheduler.get_jobs():
            job_info = {
                "job_id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "last_run_time": None,
                "last_run_status": None,
                "last_run_duration": None
            }
            
            # Add execution history if available
            if job.id in self.job_history:
                history = self.job_history[job.id]
                job_info["last_run_time"] = history.start_time.isoformat() if history.start_time else None
                job_info["last_run_status"] = history.status
                job_info["last_run_duration"] = history.duration_seconds
            
            jobs_info.append(job_info)
        
        # Calculate execution statistics
        total_executions = len(self.job_history)
        failed_executions = sum(1 for h in self.job_history.values() if h.status == "failed")
        
        return {
            "running": self.scheduler.running,
            "jobs": jobs_info,
            "total_executions": total_executions,
            "failed_executions": failed_executions
        }
