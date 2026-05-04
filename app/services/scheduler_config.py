"""
Scheduler configuration management.
Loads scheduler settings from environment variables with SCHEDULER_ prefix.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class SchedulerConfig(BaseSettings):
    """Scheduler configuration loaded from environment variables."""
    
    enabled: bool = Field(default=True)
    timezone: str = Field(default="UTC")
    misfire_grace_time: int = Field(default=60)
    shutdown_timeout: int = Field(default=30)
    job_store_type: str = Field(default="memory")
    job_store_url: Optional[str] = Field(default=None)
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = "SCHEDULER_"
        extra = "ignore"  # Ignore extra fields from environment
