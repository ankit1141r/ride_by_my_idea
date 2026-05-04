"""
Job executor for background tasks.
Handles job execution with error handling, session management, and logging.
"""
import logging
import traceback
from datetime import datetime
from typing import Callable, Any, Optional
from sqlalchemy.orm import Session

from app.database import SessionLocal

logger = logging.getLogger(__name__)


class JobExecutor:
    """Executes background jobs with proper error handling and session management."""
    
    @staticmethod
    def execute_job(
        job_name: str,
        job_func: Callable,
        *args,
        **kwargs
    ) -> Optional[Any]:
        """
        Execute a background job with error handling and logging.
        
        This method:
        1. Creates a new database session at the start
        2. Logs job start with job name and timestamp
        3. Executes the job function
        4. Commits the session on success
        5. Logs success with duration and result
        6. Catches exceptions, rollbacks session, logs error with traceback
        7. Always closes session in finally block
        8. Never re-raises exceptions (lets scheduler continue)
        
        Args:
            job_name: Name of the job being executed
            job_func: The job function to execute
            *args: Positional arguments to pass to job_func
            **kwargs: Keyword arguments to pass to job_func
        
        Returns:
            Result from job_func on success, None on failure
        
        Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 11.1, 11.2, 11.3, 11.4, 11.5,
                     13.1, 13.2, 13.3, 13.4, 13.5
        """
        session: Optional[Session] = None
        start_time = datetime.utcnow()
        
        try:
            # Log job start (Requirement 11.1)
            logger.info(f"Starting job: {job_name} at {start_time.isoformat()}")
            
            # Create new database session (Requirement 13.1)
            session = SessionLocal()
            
            # Execute the job function
            result = job_func(session, *args, **kwargs)
            
            # Commit the session on success (Requirement 13.2)
            session.commit()
            
            # Calculate duration and log success (Requirements 11.2, 11.4)
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            logger.info(
                f"Job {job_name} completed successfully in {duration:.2f}s. "
                f"Result: {result}"
            )
            
            return result
            
        except Exception as e:
            # Rollback session on error (Requirement 13.3)
            if session:
                session.rollback()
            
            # Calculate duration and log error with full traceback (Requirements 10.1, 10.2, 10.5, 11.3, 11.5)
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            error_traceback = traceback.format_exc()
            
            logger.error(
                f"Job {job_name} failed after {duration:.2f}s. "
                f"Error: {str(e)}\n"
                f"Traceback:\n{error_traceback}"
            )
            
            # Do not re-raise exception - allow scheduler to continue (Requirement 10.3)
            return None
            
        finally:
            # Always close session (Requirements 13.2, 13.3, 13.4)
            if session:
                session.close()
