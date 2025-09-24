"""
Configuration management for the Chat Application.
Centralizes all environment variables and settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24))
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database Configuration
    DB_USER = os.environ.get('DB_USER', 'chatapp_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'chatapp_password')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'chatapp_db')
    
    # Construct database URL
    DATABASE_URL = os.environ.get(
        'DATABASE_URL',
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
    # Redis Configuration
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_URL = os.environ.get('REDIS_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}')
    
    # RabbitMQ Configuration
    RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
    RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'admin')
    RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD', 'admin123')
    RABBITMQ_URL = os.environ.get(
        'RABBITMQ_URL',
        f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'
    )

class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DATABASE_URL = 'sqlite:///test.db'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}