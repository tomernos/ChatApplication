"""
Chat routes for the Chat Application.
Handles chat functionality and real-time messaging.
Pure JSON API for React frontend.
"""
from flask import Blueprint, request, jsonify, session
from app.services.database import db_service
from app.services.redis_service import redis_service
from app.services.queue_service import queue_service

# Create blueprint for chat routes
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/messages', methods=['GET'])
def get_messages():
    """
    Get all chat messages as JSON.
    This is the PRIMARY endpoint React uses to fetch messages.
    """
    # Check authentication
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Fetch all messages from database
    messages = db_service.get_all_messages()
    
    # Convert to JSON format
    messages_list = []
    for msg in messages:
        messages_list.append({
            'id': msg.id if hasattr(msg, 'id') else None,
            'user_id': msg.user_id if hasattr(msg, 'user_id') else None,
            'username': msg.username,
            'content': msg.message,  # Note: database field is 'message' but React expects 'content'
            'created_at': msg.timestamp.isoformat() if hasattr(msg, 'timestamp') and msg.timestamp else None
        })
    
    return jsonify({
        'success': True,
        'messages': messages_list,
        'count': len(messages_list)
    }), 200

@chat_bp.route('/send', methods=['POST'])
def send_message():
    """
    Send a new chat message.
    JSON API only - for React frontend.
    """
    # Check authentication
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    username = session['username']
    user_id = session.get('user_id')
    
    # Get message content from JSON
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request format'}), 400
    
    message = data.get('content')
    
    # Validate message
    if not message or not message.strip():
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Save message to database
    if db_service.create_chat_message(username, message):
        # Update message count in Redis cache
        if redis_service.is_available():
            redis_service.increment_message_count(username)
        
        # Queue message for processing (asynchronous)
        if queue_service.is_available():
            queue_service.queue_message_processing({
                'username': username,
                'message': message,
                'user_id': user_id
            })
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Message sent successfully',
            'data': {
                'username': username,
                'content': message
            }
        }), 201
    else:
        # Failed to save message
        return jsonify({'error': 'Failed to send message'}), 500

@chat_bp.route('/message/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """
    Delete a specific chat message.
    Only the message owner can delete their message.
    """
    # Check authentication
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    username = session['username']
    
    # Get the message to verify ownership
    message = db_service.get_message_by_id(message_id)
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    # Check if user owns the message
    if message.username != username:
        return jsonify({'error': 'You can only delete your own messages'}), 403
    
    # Delete the message
    if db_service.delete_message(message_id):
        return jsonify({
            'success': True,
            'message': 'Message deleted successfully'
        }), 200
    else:
        return jsonify({'error': 'Failed to delete message'}), 500

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