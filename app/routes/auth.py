"""
Authentication routes for the Chat Application.
Handles login, logout, and user registration.
Pure JSON API for React frontend.
"""
from flask import Blueprint, request, session, jsonify
from datetime import datetime
from app.services.database import db_service
from app.services.redis_service import redis_service
from app.services.queue_service import queue_service
import uuid

# Create blueprint for auth routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Handle user login.
    JSON API only - for React frontend.
    """
    # Get credentials from JSON
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request format'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    # Validate input
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Verify user credentials using database service
    user = db_service.verify_user(username, password)
    if user:
        # Create session
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        session['username'] = username
        session['user_id'] = user.id  # Store user ID for later use
        
        # Store session in Redis if available
        if redis_service.is_available():
            user_data = {
                'username': username,
                'user_id': user.id,
                'login_time': str(datetime.now()),
                'session_id': session_id
            }
            redis_service.store_session(session_id, user_data)
            redis_service.add_online_user(username)
        
        # Log user activity to message queue
        if queue_service.is_available():
            queue_service.log_user_activity(
                username, 
                'login', 
                {'session_id': session_id, 'ip': request.remote_addr}
            )
        
        # Return JSON response for React
        return jsonify({
            'success': True,
            'message': f'Welcome back, {username}!',
            'token': session_id,  # Using session_id as token
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
    else:
        # Invalid credentials
        if queue_service.is_available():
            queue_service.log_user_activity(
                username or 'unknown', 
                'failed_login', 
                {'ip': request.remote_addr}
            )
        
        return jsonify({'error': 'Invalid username or password'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Handle user logout.
    JSON API only - for React frontend.
    """
    username = session.get('username')
    session_id = session.get('session_id')
    
    # Remove user from online list and clear session from Redis
    if username and redis_service.is_available():
        redis_service.remove_online_user(username)
        if session_id:
            redis_service.delete_session(session_id)
    
    # Log user activity
    if username and queue_service.is_available():
        queue_service.log_user_activity(username, 'logout', {'session_id': session_id})
    
    # Clear Flask session
    session.clear()
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Handle user registration.
    JSON API only - for React frontend.
    """
    # Get data from JSON
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request format'}), 400
    
    # React doesn't need user_id - generate it automatically
    user_id = str(uuid.uuid4())[:8]  # Generate short unique ID
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    age = data.get('age')
    
    # Validate required fields
    if not all([username, password, email]):
        return jsonify({'error': 'Username, password, and email are required'}), 400
    
    # Validate username length
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters long'}), 400
    
    # Validate password length
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    
    # Convert age to integer if provided
    age_int = None
    if age:
        try:
            age_int = int(age)
        except (ValueError, TypeError):
            return jsonify({'error': 'Age must be a valid number'}), 400
    
    # Create user in database
    if db_service.create_user(user_id, username, password, 'A', age_int, email):
        # Send welcome email via message queue
        if queue_service.is_available():
            queue_service.queue_email_notification(
                email,
                'Welcome to ConnectHub!',
                f'Hello {username}, welcome to our chat application!'
            )
            
            # Log registration activity
            queue_service.log_user_activity(
                username, 
                'registration', 
                {'email': email, 'ip': request.remote_addr}
            )
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Registration successful! You can now log in.',
            'user': {
                'id': user_id,
                'username': username,
                'email': email
            }
        }), 201  # 201 = Created
    else:
        # Registration failed - username or email already exists
        return jsonify({'error': 'Registration failed. Username or email might already exist.'}), 409  # 409 = Conflict

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """
    Get current user profile.
    API endpoint for React to fetch logged-in user info.
    """
    # Check if user is logged in
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    username = session.get('username')
    user = db_service.get_user_by_username(username)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user statistics from Redis if available
    message_count = 0
    if redis_service.is_available():
        message_count = redis_service.get_message_count(username)
    
    # Return user data as JSON
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'age': user.age,
            'created_at': user.date.isoformat() if hasattr(user, 'date') and user.date else None,
            'message_count': message_count
        }
    }), 200