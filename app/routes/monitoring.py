"""
Monitoring Routes Blueprint
Exposes /metrics endpoint for Prometheus scraping.
"""
from flask import Blueprint
from app.services.monitoring_service import monitoring_service

# Create blueprint for monitoring routes
monitoring_bp = Blueprint('monitoring', __name__)


@monitoring_bp.route('/metrics', methods=['GET'])
def metrics():
    """
    Prometheus metrics endpoint.
    Returns metrics in Prometheus text format.
    
    This endpoint is scraped by Prometheus every 15 seconds.
    """
    return monitoring_service.get_metrics()


@monitoring_bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint (already exists in main.py, but good practice to have here too).
    Used by Kubernetes liveness probe.
    """
    return {'status': 'healthy', 'service': 'monitoring'}, 200
