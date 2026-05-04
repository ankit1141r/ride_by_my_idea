# Implementation Plan: Background Task Scheduler

## Overview

This implementation adds APScheduler-based task scheduling to execute the existing BackgroundJobService methods at appropriate intervals. The scheduler integrates with FastAPI's lifespan events for proper startup/shutdown management, includes comprehensive error handling and logging, and provides an admin API endpoint for monitoring scheduler status.

## Tasks

- [x] 1. Install and configure APScheduler dependencies
  - Add APScheduler and pytz to requirements.txt with version specifications
  - Verify imports work correctly
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 2. Create scheduler configuration module
  - [x] 2.1 Create app/services/scheduler_config.py with SchedulerConfig model
    - Define configuration model with environment variable support
    - Include settings for timezone, misfire_grace_time, shutdown_timeout, job_store_type
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 14.3, 14.4, 14.5_
  
  - [ ]* 2.2 Write unit tests for scheduler configuration
    - Test configuration loading from environment variables
    - Test default values
    - Test validation of configuration parameters
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 3. Implement JobExecutor with error handling and session management
  - [x] 3.1 Create app/services/job_executor.py with JobExecutor class
    - Implement execute_job method with try-except-finally structure
    - Create and manage database sessions for each job execution
    - Implement comprehensive logging (start, success, failure)
    - Ensure session cleanup on both success and failure paths
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 11.1, 11.2, 11.3, 11.4, 11.5, 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [ ]* 3.2 Write property test for job execution error isolation
    - **Property 1: Job Execution Error Isolation**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.5**
    - Test that exceptions are caught and logged without propagating to scheduler
    - Use hypothesis to generate random job names and exception types
    - _Requirements: 10.1, 10.2, 10.3, 10.5_
  
  - [ ]* 3.3 Write property test for comprehensive job execution logging
    - **Property 2: Comprehensive Job Execution Logging**
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5**
    - Test that all executions are logged with appropriate details and levels
    - Use hypothesis to generate random job names and success/failure scenarios
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [ ]* 3.4 Write property test for database session lifecycle management
    - **Property 3: Database Session Lifecycle Management**
    - **Validates: Requirements 13.1, 13.2, 13.3, 13.5**
    - Test that sessions are created, committed/rolled back, and closed correctly
    - Use hypothesis to generate random job names and success/failure scenarios
    - Verify no session reuse across executions
    - _Requirements: 13.1, 13.2, 13.3, 13.5_
  
  - [ ]* 3.5 Write unit tests for JobExecutor
    - Test successful job execution with mocked BackgroundJobService
    - Test job execution with exception
    - Test database session creation and cleanup
    - Test logging output for success and failure cases
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 11.1, 11.2, 11.3, 13.1, 13.2, 13.3_

- [ ] 4. Implement SchedulerService with job registration
  - [x] 4.1 Create app/services/scheduler_service.py with SchedulerService class
    - Initialize AsyncIOScheduler with configuration
    - Implement start() method to initialize and start scheduler
    - Implement shutdown() method with graceful timeout handling
    - Implement register_jobs() method to register all 6 background jobs
    - Implement get_status() method to return scheduler and job information
    - Track job execution history in job_history dictionary
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [x] 4.2 Register all background jobs with correct schedules
    - Register check_insurance_expiry (daily at 00:00 UTC, cron trigger)
    - Register check_route_deviations (every 30 seconds, interval trigger)
    - Register reset_daily_cancellation_counts (daily at 00:00 UTC, cron trigger)
    - Register unsuspend_drivers_after_24_hours (every hour, interval trigger)
    - Register reset_daily_availability_hours (daily at 00:00 UTC, cron trigger)
    - Register process_scheduled_rides (every minute, interval trigger)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3, 6.4, 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4, 9.1, 9.2, 9.3, 9.4_
  
  - [ ]* 4.3 Write unit tests for SchedulerService
    - Test scheduler initialization with correct configuration
    - Test job registration (verify all 6 jobs are registered)
    - Test correct schedule for each job (cron vs interval, timing parameters)
    - Test scheduler startup and shutdown
    - Test get_status() method response
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 4.1, 5.1, 6.1, 7.1, 8.1, 9.1_

- [ ] 5. Integrate scheduler with FastAPI lifespan events
  - [x] 5.1 Modify app/main.py to add lifespan context manager
    - Create lifespan async context manager function
    - Initialize and start SchedulerService on startup
    - Shutdown SchedulerService gracefully on application shutdown
    - Pass lifespan to FastAPI app initialization
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [ ]* 5.2 Write integration tests for scheduler lifecycle
    - Test full application lifecycle with scheduler (startup, operation, shutdown)
    - Test scheduler starts when application starts
    - Test scheduler stops when application shuts down
    - Test graceful shutdown with running jobs
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 15.1, 15.2, 15.3_

- [ ] 6. Implement admin API endpoint for scheduler status
  - [x] 6.1 Create app/schemas/scheduler.py with response models
    - Define JobInfo model with job details
    - Define SchedulerStatusResponse model
    - _Requirements: 12.2, 12.3, 12.4, 12.5_
  
  - [x] 6.2 Add scheduler status endpoint to app/routers/admin.py
    - Create GET /admin/scheduler/status endpoint
    - Require admin authentication
    - Return scheduler running state and job information
    - Include next run times and last execution details
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [ ]* 6.3 Write unit tests for scheduler status endpoint
    - Test endpoint response structure
    - Test authentication requirement (reject non-admin users)
    - Test status response includes all registered jobs
    - Test status response includes next run times and execution history
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 7. Add job persistence support (optional for production)
  - [ ] 7.1 Implement SQLAlchemy job store configuration
    - Add conditional job store initialization based on configuration
    - Support both in-memory (development) and SQLAlchemy (production) stores
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_
  
  - [ ]* 7.2 Write tests for job persistence
    - Test in-memory job store configuration
    - Test SQLAlchemy job store configuration
    - Test job restoration after restart with persistent store
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [x] 8. Checkpoint - Verify scheduler functionality
  - Run the application and verify scheduler starts successfully
  - Check logs to confirm jobs are being executed at correct intervals
  - Test admin API endpoint to verify scheduler status
  - Ensure all tests pass
  - Ask the user if questions arise

- [ ] 9. Update documentation
  - Add scheduler configuration to README.md or deployment documentation
  - Document environment variables for scheduler configuration
  - Document admin API endpoint usage
  - _Requirements: All_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- The scheduler uses existing BackgroundJobService methods without modification
- All background jobs use the same error handling and logging patterns
- Database sessions are created fresh for each job execution to avoid connection issues
- Graceful shutdown ensures running jobs complete before application stops
- Property tests validate universal correctness properties across all job executions
- Unit tests validate specific examples and edge cases for each component
