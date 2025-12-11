"""
Prometheus Monitoring Service
Provides metrics collection for the application.

Metrics exposed:
- http_requests_total: Total HTTP requests (counter)
- http_request_duration_seconds: Request latency (histogram)
- http_requests_in_progress: Requests currently being processed (gauge)
"""
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import request, g
import logging

logger = logging.getLogger(__name__)

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently being processed',
    ['method', 'endpoint']
)

# Custom business metrics (optional - add your own!)
# Example: chat_messages_sent_total = Counter('chat_messages_sent_total', 'Total chat messages sent')


class MonitoringService:
    """Service for tracking application metrics."""
    
    @staticmethod
    def before_request():
        """
        Called before each request.
        Records start time and increments in-progress counter.
        """
        g.start_time = time.time()
        
        # Track concurrent requests
        endpoint = request.endpoint or 'unknown'
        http_requests_in_progress.labels(
            method=request.method,
            endpoint=endpoint
        ).inc()
    
    @staticmethod
    def after_request(response):
        """
        Called after each request.
        Records metrics: duration, status code, decrements in-progress counter.
        """
        # Calculate request duration
        if hasattr(g, 'start_time'):
            request_latency = time.time() - g.start_time
        else:
            request_latency = 0
        
        endpoint = request.endpoint or 'unknown'
        
        # Record metrics
        http_requests_total.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(request_latency)
        
        # Decrement in-progress counter
        http_requests_in_progress.labels(
            method=request.method,
            endpoint=endpoint
        ).dec()
        
        return response
    
    @staticmethod
    def get_metrics():
        """
        Returns Prometheus metrics in text format.
        This is what Prometheus scrapes.
        """
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    
    @staticmethod
    def register_middleware(app):
        """
        Register monitoring middleware with Flask app.
        Call this in your app factory.
        """
        app.before_request(MonitoringService.before_request)
        app.after_request(MonitoringService.after_request)
        logger.info("✅ Monitoring middleware registered")


# Singleton instance
monitoring_service = MonitoringService()
