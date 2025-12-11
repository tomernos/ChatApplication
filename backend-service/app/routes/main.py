"""
Main routes for the Chat Application.
API health check and status endpoints for Kubernetes.
"""
from flask import Blueprint, jsonify
from app.services.database import db_service
from app.services.redis_service import redis_service
from app.services.queue_service import queue_service

# Create blueprint for main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    API root endpoint - returns API information and available endpoints.
    Useful for API discovery and documentation.
    """
    return jsonify({
        'status': 'ok',
        'service': 'ConnectHub Chat API',
        'version': '1.0.0',
        'description': 'RESTful API for ConnectHub Chat Application',
        'endpoints': {
            'health': '/ health',
            'readiness': '/ready',
            'auth': {
                'login': '/api/auth/login [POST]',
                'register': '/api/auth/register [POST]',
                'logout': '/api/auth/logout [POST]',
                'profile': '/api/auth/profile [GET]'
            },
            'chat': {
                'messages': '/api/chat/messages [GET]',
                'send': '/api/chat/send [POST]',
                'delete': '/api/chat/message/<id> [DELETE]'
            },
            'users': {
                'list': '/api/users [GET]',
                'get': '/api/users/<id> [GET]',
                'update': '/api/users/<id> [PUT]',
                'delete': '/api/users/<id> [DELETE]',
                'online': '/api/users/online [GET]'
            }
        }
    }), 200

@main_bp.route('/health')
def health():
    """
    Liveness probe for Kubernetes.
    
    Returns 200 if the application is running (process is alive).
    Kubernetes will restart the pod if this returns non-200 or times out.
    
    This is a simple check - just confirms Flask is responding.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'ConnectHub Chat API',
        'message': 'Application is running'
    }), 200

@main_bp.route('/ready')
def ready():
    """
    Readiness probe for Kubernetes.
    
    Returns 200 only if the application is ready to serve traffic.
    Checks if critical dependencies are available:
    - Database connection
    - Redis (optional but check availability)
    - RabbitMQ (optional but check availability)
    
    Kubernetes won't send traffic to this pod if this returns non-200.
    """
    health_status = {
        'status': 'ready',
        'service': 'ConnectHub Chat API',
        'dependencies': {}
    }
    
    # Check database connectivity
    try:
        user_count = db_service.count_users()
        health_status['dependencies']['database'] = {
            'status': 'connected',
            'type': 'PostgreSQL',
            'users': user_count
        }
    except Exception as e:
        health_status['status'] = 'not_ready'
        health_status['dependencies']['database'] = {
            'status': 'error',
            'error': str(e)
        }
        return jsonify(health_status), 503  # 503 Service Unavailable
    
    # Check Redis (optional - won't fail readiness if unavailable)
    health_status['dependencies']['redis'] = {
        'status': 'connected' if redis_service.is_available() else 'unavailable',
        'type': 'Redis',
        'optional': True
    }
    
    # Check RabbitMQ (optional - won't fail readiness if unavailable)
    health_status['dependencies']['rabbitmq'] = {
        'status': 'connected' if queue_service.is_available() else 'unavailable',
        'type': 'RabbitMQ',
        'optional': True
    }
    
    return jsonify(health_status), 200