"""
Chat routes for the Chat Application.
Handles chat functionality and real-time messaging.
"""
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from app.services.database import db_service
from app.services.redis_service import redis_service
from app.services.queue_service import queue_service

# Create blueprint for chat routes
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/', methods=['GET', 'POST'])
def chat_room():
    """Main chat room page."""
    if 'username' not in session:
        flash('Please log in to access chat')
        return redirect(url_for('auth.login'))
    
    # Handle message sending via POST
    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            username = session['username']
            if db_service.create_chat_message(username, message):
                # Update message count in Redis
                if redis_service.is_available():
                    redis_service.increment_message_count(username)
                flash('Message sent successfully!')
            else:
                flash('Failed to send message')
        return redirect(url_for('chat.chat_room'))
    
    # Get chat messages
    messages = db_service.get_all_messages()
    
    # Get online users
    online_users = []
    if redis_service.is_available():
        online_users = redis_service.get_online_users()
    
    return render_template('chat.html', messages=messages, online_users=online_users, current_user=session['username'])

@chat_bp.route('/send', methods=['POST'])
def send_message():
    """Send a chat message."""
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    username = session['username']
    message = request.form.get('message') or request.json.get('message')
    
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Save message to database
    if db_service.create_chat_message(username, message):
        # Update message count in Redis
        if redis_service.is_available():
            redis_service.increment_message_count(username)
        
        # Queue message for processing
        if queue_service.is_available():
            queue_service.queue_message_processing({
                'username': username,
                'message': message
            })
        
        return jsonify({'success': True, 'message': 'Message sent'})
    else:
        return jsonify({'error': 'Failed to send message'}), 500

@chat_bp.route('/messages')
def get_messages():
    """Get all chat messages as JSON."""
    messages = db_service.get_all_messages()
    return jsonify([{
        'username': msg.username,
        'message': msg.message,
        'timestamp': msg.timestamp.isoformat()
    } for msg in messages])

@chat_bp.route('/typing', methods=['POST'])
def set_typing():
    """Set typing indicator for current user."""
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    username = session['username']
    
    if redis_service.is_available():
        redis_service.set_typing_indicator(username)
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Redis not available'}), 503

@chat_bp.route('/typing')
def get_typing():
    """Get users currently typing."""
    if redis_service.is_available():
        typing_users = redis_service.get_typing_users()
        current_user = session.get('username')
        # Remove current user from typing list
        if current_user in typing_users:
            typing_users.remove(current_user)
        return jsonify({'typing_users': typing_users})
    else:
        return jsonify({'typing_users': []})