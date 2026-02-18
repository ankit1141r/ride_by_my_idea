"""
Request logging middleware.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
import uuid

from app.utils.metrics import metrics_collector

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        """
        Log request and response details.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        
        logger.info(
            f"Request started | "
            f"ID: {request_id} | "
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            metrics_collector.record_request(
                endpoint=f"{request.method} {request.url.path}",
                duration=duration,
                status_code=response.status_code
            )
            
            # Log response
            logger.info(
                f"Request completed | "
                f"ID: {request_id} | "
                f"Status: {response.status_code} | "
                f"Duration: {duration:.3f}s"
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Record error metric
            metrics_collector.record_request(
                endpoint=f"{request.method} {request.url.path}",
                duration=duration,
                status_code=500
            )
            
            logger.error(
                f"Request failed | "
                f"ID: {request_id} | "
                f"Error: {str(e)} | "
                f"Duration: {duration:.3f}s",
                exc_info=True
            )
            raise
