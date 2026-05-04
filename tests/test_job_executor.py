"""
Tests for JobExecutor class.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.services.job_executor import JobExecutor


class TestJobExecutor:
    """Test suite for JobExecutor."""
    
    def test_successful_job_execution(self):
        """Test that a successful job executes correctly with proper session management."""
        # Create a mock job function
        mock_job = Mock(return_value="success_result")
        
        # Mock SessionLocal
        with patch('app.services.job_executor.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            # Execute job
            result = JobExecutor.execute_job("test_job", mock_job, "arg1", kwarg1="value1")
            
            # Verify job was called with session and arguments
            mock_job.assert_called_once_with(mock_session, "arg1", kwarg1="value1")
            
            # Verify session was committed and closed
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()
            mock_session.rollback.assert_not_called()
            
            # Verify result
            assert result == "success_result"
    
    def test_job_execution_with_exception(self):
        """Test that exceptions are caught and session is rolled back."""
        # Create a mock job function that raises an exception
        mock_job = Mock(side_effect=ValueError("Test error"))
        
        # Mock SessionLocal
        with patch('app.services.job_executor.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            # Execute job (should not raise exception)
            result = JobExecutor.execute_job("test_job", mock_job)
            
            # Verify job was called
            mock_job.assert_called_once()
            
            # Verify session was rolled back and closed
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()
            mock_session.commit.assert_not_called()
            
            # Verify result is None on failure
            assert result is None
    
    def test_job_execution_logging_success(self, caplog):
        """Test that successful job execution is logged at INFO level."""
        import logging
        caplog.set_level(logging.INFO)
        
        # Create a mock job function
        mock_job = Mock(return_value=42)
        
        # Mock SessionLocal
        with patch('app.services.job_executor.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            # Execute job
            JobExecutor.execute_job("test_success_job", mock_job)
            
            # Verify logging
            assert "Starting job: test_success_job" in caplog.text
            assert "test_success_job completed successfully" in caplog.text
            assert "Result: 42" in caplog.text
    
    def test_job_execution_logging_failure(self, caplog):
        """Test that failed job execution is logged at ERROR level with traceback."""
        import logging
        caplog.set_level(logging.ERROR)
        
        # Create a mock job function that raises an exception
        mock_job = Mock(side_effect=RuntimeError("Test failure"))
        
        # Mock SessionLocal
        with patch('app.services.job_executor.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            # Execute job
            JobExecutor.execute_job("test_failure_job", mock_job)
            
            # Verify error logging
            assert "test_failure_job failed" in caplog.text
            assert "Error: Test failure" in caplog.text
            assert "Traceback:" in caplog.text
    
    def test_session_cleanup_on_exception_before_session_creation(self):
        """Test that session cleanup handles case where session creation fails."""
        # Mock SessionLocal to raise an exception
        with patch('app.services.job_executor.SessionLocal', side_effect=Exception("DB connection failed")):
            mock_job = Mock()
            
            # Execute job (should not raise exception)
            result = JobExecutor.execute_job("test_job", mock_job)
            
            # Verify job was not called (session creation failed)
            mock_job.assert_not_called()
            
            # Verify result is None
            assert result is None
    
    def test_multiple_job_executions_use_different_sessions(self):
        """Test that each job execution creates a new session."""
        mock_job = Mock(return_value="result")
        
        # Mock SessionLocal to return different sessions
        with patch('app.services.job_executor.SessionLocal') as mock_session_local:
            session1 = MagicMock()
            session2 = MagicMock()
            mock_session_local.side_effect = [session1, session2]
            
            # Execute job twice
            JobExecutor.execute_job("job1", mock_job)
            JobExecutor.execute_job("job2", mock_job)
            
            # Verify both sessions were created and closed
            assert mock_session_local.call_count == 2
            session1.close.assert_called_once()
            session2.close.assert_called_once()
