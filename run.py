"""
Main entry point for the Chat Application.
Run this file to start the Flask development server.
"""
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Chat Application...")
    print("📍 Available at: http://localhost:5000")
    print("🔧 Environment: Development")
    print("💾 Database: PostgreSQL")
    print("⚡ Cache: Redis (if available)")
    print("📬 Queue: RabbitMQ (if available)")
    print("-" * 50)
    
    # Get debug setting from environment
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=debug_mode,
        use_debugger=False,  # Disable interactive debugger
        use_reloader=True    # Keep auto-reload for development
    )