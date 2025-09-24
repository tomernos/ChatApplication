"""
Flask application factory and initialization.
Creates and configures the Flask application with all blueprints and services.
"""
import os
from flask import Flask, render_template, session
from config import config
from app.models import create_tables
from app.services.redis_service import redis_service
from app.services.queue_service import queue_service, handle_email_notification, handle_activity_log

def create_app(config_name=None):
    """Application factory pattern for creating Flask app."""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask application with correct template path
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize database
    with app.app_context():
        create_tables()
        print("Application initialized successfully!")
    
    # Start background workers if services are available
    if queue_service.is_available():
        queue_service.start_email_worker(handle_email_notification)
        queue_service.start_activity_logger(handle_activity_log)
        print("Background workers started successfully!")
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.chat import chat_bp
    from app.routes.user import user_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(user_bp, url_prefix='/user')
    
    # Context processors for templates
    @app.context_processor
    def inject_user():
        """Inject user information into all templates."""
        username = session.get('username')
        online_users = []
        
        if username and redis_service.is_available():
            online_users = redis_service.get_online_users()
        
        return {
            'current_user': username,
            'online_users': online_users,
            'redis_available': redis_service.is_available(),
            'queue_available': queue_service.is_available()
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error='Page not found'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', error='Internal server error'), 500
    
    return app

# For direct execution
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)