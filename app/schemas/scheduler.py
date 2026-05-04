"""
Scheduler response models for admin API endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class JobInfo(BaseModel):
    """
    Information about a scheduled job.
    
    Requirements: 12.3, 12.4
    """
    job_id: str = Field(..., description="Unique identifier for the job")
    name: str = Field(..., description="Human-readable job name")
    next_run_time: Optional[datetime] = Field(None, description="Next scheduled execution time")
    last_run_time: Optional[datetime] = Field(None, description="Last execution time")
    last_run_status: Optional[str] = Field(None, description="Status of last execution (success/failed)")
    last_run_duration: Optional[float] = Field(None, description="Duration of last execution in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "check_insurance_expiry",
                "name": "Check Insurance Expiry",
                "next_run_time": "2024-01-15T00:00:00",
                "last_run_time": "2024-01-14T00:00:00",
                "last_run_status": "success",
                "last_run_duration": 2.5
            }
        }


class SchedulerStatusResponse(BaseModel):
    """
    Response model for scheduler status endpoint.
    
    Requirements: 12.2, 12.3, 12.4
    """
    running: bool = Field(..., description="Whether the scheduler is currently running")
    jobs: List[JobInfo] = Field(..., description="List of registered jobs with their details")
    total_executions: int = Field(..., description="Total number of job executions")
    failed_executions: int = Field(..., description="Number of failed job executions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "running": True,
                "jobs": [
                    {
                        "job_id": "check_insurance_expiry",
                        "name": "Check Insurance Expiry",
                        "next_run_time": "2024-01-15T00:00:00",
                        "last_run_time": "2024-01-14T00:00:00",
                        "last_run_status": "success",
                        "last_run_duration": 2.5
                    }
                ],
                "total_executions": 150,
                "failed_executions": 3
            }
        }
