#!/usr/bin/env python3
"""
Auth Service - Microservice for Authentication & Authorization
Handles: Login, Register, Sessions, JWT Tokens
Port: 3001
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'auth-service-secret-key')
CORS(app)

# Configuration
DATABASE_URL = os.environ.get('AUTH_DB_URL', 'postgresql://auth_user:auth_pass@localhost:5432/auth_db')
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
JWT_SECRET = os.environ.get('JWT_SECRET', 'jwt-secret-key')

# Initialize Redis
try:
    redis_client = redis.Redis.from_url(REDIS_URL)
    redis_client.ping()
    logger.info("✅ Connected to Redis")
except Exception as e:
    logger.error(f"❌ Redis connection failed: {e}")
    redis_client = None

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def create_tables():
    """Create auth tables if they don't exist"""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS auth_users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES auth_users(id),
                    session_token VARCHAR(255) UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                conn.commit()
                logger.info("✅ Auth database tables created/verified")
        except Exception as e:
            logger.error(f"Table creation error: {e}")
        finally:
            conn.close()

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Service health check"""
    return jsonify({
        'service': 'auth-service',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200

# Register endpoint
@app.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        # Hash password
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                INSERT INTO auth_users (username, email, password_hash, first_name, last_name)
                VALUES (%s, %s, %s, %s, %s) RETURNING id, username, email, first_name, last_name
                """, (username, email, password_hash, first_name, last_name))
                
                user = cur.fetchone()
                conn.commit()

                logger.info(f"✅ User registered: {username}")
                return jsonify({
                    'success': True,
                    'message': 'User registered successfully',
                    'user': dict(user)
                }), 201

        except psycopg2.IntegrityError as e:
            conn.rollback()
            if 'username' in str(e):
                return jsonify({'error': 'Username already exists'}), 409
            elif 'email' in str(e):
                return jsonify({'error': 'Email already exists'}), 409
            else:
                return jsonify({'error': 'Registration failed'}), 400
        finally:
            conn.close()

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Login endpoint
@app.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user and create session"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                SELECT id, username, email, password_hash, first_name, last_name, is_active
                FROM auth_users WHERE username = %s
                """, (username,))
                
                user = cur.fetchone()

                if user and check_password_hash(user['password_hash'], password):
                    if not user['is_active']:
                        return jsonify({'error': 'Account is deactivated'}), 403

                    # Create JWT token
                    token_payload = {
                        'user_id': user['id'],
                        'username': user['username'],
                        'exp': datetime.utcnow() + timedelta(hours=24)
                    }
                    token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')

                    # Create session in database
                    session_token = str(uuid.uuid4())
                    expires_at = datetime.utcnow() + timedelta(hours=24)
                    
                    cur.execute("""
                    INSERT INTO auth_sessions (user_id, session_token, expires_at)
                    VALUES (%s, %s, %s)
                    """, (user['id'], session_token, expires_at))
                    
                    # Update last login
                    cur.execute("""
                    UPDATE auth_users SET last_login = CURRENT_TIMESTAMP 
                    WHERE id = %s
                    """, (user['id'],))
                    
                    conn.commit()

                    # Store session in Redis for fast access
                    if redis_client:
                        session_data = {
                            'user_id': user['id'],
                            'username': user['username'],
                            'session_token': session_token
                        }
                        redis_client.setex(f"session:{session_token}", 86400, str(session_data))
                        redis_client.sadd("online_users", user['username'])

                    logger.info(f"✅ User login: {username}")
                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'token': token,
                        'session_token': session_token,
                        'user': {
                            'id': user['id'],
                            'username': user['username'],
                            'email': user['email'],
                            'first_name': user['first_name'],
                            'last_name': user['last_name']
                        }
                    }), 200
                else:
                    return jsonify({'error': 'Invalid credentials'}), 401

        finally:
            conn.close()

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Logout endpoint
@app.route('/auth/logout', methods=['POST'])
def logout():
    """Logout user and invalidate session"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401

        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            username = payload.get('username')
            
            # Remove from Redis
            if redis_client:
                redis_client.srem("online_users", username)
                # Remove session if we have session_token
                session_token = request.json.get('session_token') if request.json else None
                if session_token:
                    redis_client.delete(f"session:{session_token}")

            logger.info(f"✅ User logout: {username}")
            return jsonify({
                'success': True,
                'message': 'Logout successful'
            }), 200

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Verify token endpoint
@app.route('/auth/verify', methods=['GET'])
def verify_token():
    """Verify JWT token validity"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401

        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            return jsonify({
                'valid': True,
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'exp': payload.get('exp')
            }), 200

        except jwt.ExpiredSignatureError:
            return jsonify({'valid': False, 'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'valid': False, 'error': 'Invalid token'}), 401

    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ != '__main__':
    # This runs when imported by Gunicorn - just create tables
    create_tables()

if __name__ == '__main__':
    # This runs when called with: python3 app.py
    create_tables()
    
    # Start the service
    port = int(os.environ.get('PORT', 3001))
    logger.info(f"🚀 Auth Service starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)