"""
Flask application factory and initialization.
Creates and configures the Flask application with all blueprints and services.
Pure JSON API - no template rendering.
"""
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from app.models import create_tables
from app.services.redis_service import redis_service
from app.services.queue_service import queue_service, handle_email_notification, handle_activity_log

# OpenTelemetry imports for distributed tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource

# Simple logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def _initialize_opentelemetry():
    """Initialize OpenTelemetry for distributed tracing."""
    try:
        # Get configuration from environment variables
        otel_endpoint_raw = os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4317"
        )
        service_name = os.getenv("OTEL_SERVICE_NAME", "chatapp-backend")
        
        # OTLPSpanExporter for gRPC expects endpoint without http:// prefix
        # Strip http:// or https:// if present
        if otel_endpoint_raw.startswith("http://"):
            otel_endpoint = otel_endpoint_raw.replace("http://", "", 1)
        elif otel_endpoint_raw.startswith("https://"):
            otel_endpoint = otel_endpoint_raw.replace("https://", "", 1)
        else:
            otel_endpoint = otel_endpoint_raw
        
        # Create resource with service information (matching example pattern)
        resource = Resource.create({
            "service.name": service_name,
        })
        
        # Create and set tracer provider (matching example pattern)
        trace_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(trace_provider)
        
        # Configure OTLP exporter (sends traces to OTEL Collector)
        # gRPC endpoint should be host:port format (no http:// prefix)
        otlp_exporter = OTLPSpanExporter(
            endpoint=otel_endpoint,
            insecure=True  # For dev, use TLS in prod
        )
        
        # Add the exporter to the tracer provider (matching example pattern)
        trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        
        logger.info(f"✅ OpenTelemetry initialized: {service_name} -> {otel_endpoint}")
    except Exception as e:
        logger.warning(f"⚠️  Failed to initialize OpenTelemetry: {e}. Tracing disabled.")
        import traceback
        logger.warning(f"   Error details: {traceback.format_exc()}")

def create_app(config_name=None):
    """Application factory pattern for creating Flask app."""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Initialize OpenTelemetry before creating Flask app
    _initialize_opentelemetry()
    
    # Create Flask application (no templates needed - pure API)
    app = Flask(__name__)
    
    # Auto-instrument Flask and requests with OpenTelemetry (matching example pattern)
    try:
        FlaskInstrumentor().instrument_app(app)
        RequestsInstrumentor().instrument()
        logger.info("✅ Flask and Requests OpenTelemetry instrumentation enabled")
    except Exception as e:
        logger.warning(f"⚠️  Failed to instrument Flask/Requests: {e}")
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    logger.info(f"Starting ConnectHub in {config_name} mode")
    
    # Enable CORS for React frontend
    # This allows React (localhost:3000) to make requests to Flask (localhost:5000)
    CORS(app, 
         origins=['http://localhost:3000', 'http://localhost:80'],
         supports_credentials=True,  # Allow cookies/sessions
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Initialize database
    with app.app_context():
        try:
            create_tables()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database init failed: {e}")
            raise
    
    # Start background workers if available
    if queue_service.is_available():
        queue_service.start_email_worker(handle_email_notification)
        queue_service.start_activity_logger(handle_activity_log)
        logger.info("Background workers started")
    else:
        logger.warning("RabbitMQ unavailable - skipping workers")
    
    # Initialize monitoring (BEFORE blueprints to track all requests)
    from app.services.monitoring_service import monitoring_service
    monitoring_service.register_middleware(app)
    logger.info("Monitoring enabled - metrics at /metrics")
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.chat import chat_bp
    from app.routes.user import user_bp
    from app.routes.monitoring import monitoring_bp
    
    # API routes (for React frontend)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    
    # Monitoring routes (Prometheus scrapes this)
    app.register_blueprint(monitoring_bp)
    
    # Main routes (API status and health check)
    app.register_blueprint(main_bp)
    
    logger.info("API ready")
    
    # Error handlers - JSON only
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# For direct execution
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)