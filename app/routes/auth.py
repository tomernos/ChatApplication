"""
Authentication routes for the Chat Application.
Handles login, logout, and user registration.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from app.services.database import db_service
from app.services.redis_service import redis_service
from app.services.queue_service import queue_service
import uuid

# Create blueprint for auth routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required')
            return render_template('login.html')
        
        # Verify user credentials
        if db_service.verify_user(username, password):
            # Create session
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            session['username'] = username
            
            # Store session in Redis if available
            if redis_service.is_available():
                user_data = {
                    'username': username,
                    'login_time': str(datetime.now()),
                    'session_id': session_id
                }
                redis_service.store_session(session_id, user_data)
                redis_service.add_online_user(username)
            
            # Log user activity
            if queue_service.is_available():
                queue_service.log_user_activity(
                    username, 
                    'login', 
                    {'session_id': session_id, 'ip': request.remote_addr}
                )
            
            flash(f'Welcome back, {username}!')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password')
            
            # Log failed login attempt
            if queue_service.is_available():
                queue_service.log_user_activity(
                    username or 'unknown', 
                    'failed_login', 
                    {'ip': request.remote_addr}
                )
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Handle user logout."""
    username = session.get('username')
    session_id = session.get('session_id')
    
    if username and redis_service.is_available():
        redis_service.remove_online_user(username)
        if session_id:
            redis_service.delete_session(session_id)
    
    # Log user activity
    if username and queue_service.is_available():
        queue_service.log_user_activity(username, 'logout', {'session_id': session_id})
    
    session.clear()
    flash('You have been logged out successfully')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        age = request.form.get('age')
        
        if not all([user_id, username, password, email]):
            flash('All fields except age are required')
            return render_template('register.html')
        
        # Convert age to integer if provided
        age_int = None
        if age:
            try:
                age_int = int(age)
            except ValueError:
                flash('Age must be a valid number')
                return render_template('register.html')
        
        # Create user
        if db_service.create_user(user_id, username, password, 'A', age_int, email):
            # Send welcome email
            if queue_service.is_available():
                queue_service.queue_email_notification(
                    email,
                    'Welcome to ChatApp!',
                    f'Hello {username}, welcome to our chat application!'
                )
                
                # Log registration
                queue_service.log_user_activity(
                    username, 
                    'registration', 
                    {'email': email, 'ip': request.remote_addr}
                )
            
            flash('Registration successful! You can now log in.')
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed. Username or ID might already exist.')
    
    return render_template('register.html')