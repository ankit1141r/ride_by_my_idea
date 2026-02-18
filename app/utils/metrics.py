"""
Performance metrics and monitoring utilities.
"""
from typing import Dict, Any
from datetime import datetime
import time
from collections import defaultdict
import threading


class MetricsCollector:
    """Collect and track application metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self._lock = threading.Lock()
        self._request_counts = defaultdict(int)
        self._request_durations = defaultdict(list)
        self._error_counts = defaultdict(int)
        self._start_time = datetime.utcnow()
    
    def record_request(self, endpoint: str, duration: float, status_code: int):
        """
        Record a request metric.
        
        Args:
            endpoint: API endpoint path
            duration: Request duration in seconds
            status_code: HTTP status code
        """
        with self._lock:
            self._request_counts[endpoint] += 1
            self._request_durations[endpoint].append(duration)
            
            if status_code >= 400:
                self._error_counts[endpoint] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics summary.
        
        Returns:
            Dict containing metrics data
        """
        with self._lock:
            metrics = {
                "uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds(),
                "total_requests": sum(self._request_counts.values()),
                "total_errors": sum(self._error_counts.values()),
                "endpoints": {}
            }
            
            for endpoint in self._request_counts:
                durations = self._request_durations[endpoint]
                
                if durations:
                    avg_duration = sum(durations) / len(durations)
                    max_duration = max(durations)
                    min_duration = min(durations)
                else:
                    avg_duration = max_duration = min_duration = 0
                
                metrics["endpoints"][endpoint] = {
                    "request_count": self._request_counts[endpoint],
                    "error_count": self._error_counts[endpoint],
                    "avg_duration_ms": round(avg_duration * 1000, 2),
                    "max_duration_ms": round(max_duration * 1000, 2),
                    "min_duration_ms": round(min_duration * 1000, 2)
                }
            
            return metrics
    
    def reset_metrics(self):
        """Reset all metrics."""
        with self._lock:
            self._request_counts.clear()
            self._request_durations.clear()
            self._error_counts.clear()
            self._start_time = datetime.utcnow()


# Global metrics collector instance
metrics_collector = MetricsCollector()
