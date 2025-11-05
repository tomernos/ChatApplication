"""
User management routes for the Chat Application.
Handles user CRUD operations and profile management.
Pure JSON API for React frontend.
"""
from flask import Blueprint, request, session, jsonify
from app.services.database import db_service
from app.services.redis_service import redis_service

# Create blueprint for user routes
user_bp = Blueprint('user', __name__)

@user_bp.route('/', methods=['GET'])
def get_all_users():
    """
    Get all users as JSON.
    API endpoint for React UsersPage.
    """
    # Check authentication
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Fetch all users from database
    users = db_service.get_all_users()
    
    # Convert to JSON format
    users_list = []
    for user in users:
        users_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'age': user.age,
            'created_at': user.date.isoformat() if hasattr(user, 'date') and user.date else None
        })
    
    return jsonify({
        'success': True,
        'users': users_list,
        'count': len(users_list)
    }), 200

@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get specific user by ID.
    API endpoint for viewing user profiles.
    """
    # Check authentication
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Fetch user from database
    user = db_service.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user statistics from Redis if available
    message_count = 0
    if redis_service.is_available():
        message_count = redis_service.get_message_count(user.username)
    
    # Return user data
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

@user_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Update user information.
    JSON API only - for React frontend.
    """
    # Check authentication
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get current user and target user
    current_user = db_service.get_user_by_username(session['username'])
    target_user = db_service.get_user_by_id(user_id)
    
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check permissions (users can only modify their own profile, admins can modify any)
    if current_user.id != user_id and current_user.classification != 'A':
        return jsonify({'error': 'You can only modify your own profile'}), 403
    
    # Get update data from JSON
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request format'}), 400
    
    updates = {}
    
    # Process allowed updates
    if 'username' in data and data['username'] != target_user.username:
        updates['username'] = data['username']
    if 'email' in data and data['email'] != target_user.email:
        updates['email'] = data['email']
    if 'age' in data:
        try:
            updates['age'] = int(data['age'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Age must be a valid number'}), 400
    
    if not updates:
        return jsonify({'message': 'No changes made'}), 200
    
    # Update user in database
    if db_service.update_user(user_id, **updates):
        # Clear cached user data in Redis
        if redis_service.is_available():
            redis_service.redis_client.delete(f"user_cache:{target_user.username}")
            if updates.get('username'):
                redis_service.redis_client.delete(f"user_cache:{data['username']}")
        
        # Return updated user data
        updated_user = db_service.get_user_by_id(user_id)
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': {
                'id': updated_user.id,
                'username': updated_user.username,
                'email': updated_user.email,
                'age': updated_user.age
            }
        }), 200
    else:
        return jsonify({'error': 'Failed to update user'}), 500

@user_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete user.
    JSON API only - for React frontend.
    """
    # Check authentication
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    current_user = db_service.get_user_by_username(session['username'])
    
    # Only admins can delete users
    if current_user.classification != 'A':
        return jsonify({'error': 'Unauthorized - admin access required'}), 403
    
    # Cannot delete yourself
    if current_user.id == user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    target_user = db_service.get_user_by_id(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Delete user from database
    if db_service.delete_user(user_id):
        # Clean up Redis data
        if redis_service.is_available():
            redis_service.remove_online_user(target_user.username)
            redis_service.redis_client.delete(f"user_cache:{target_user.username}")
            redis_service.redis_client.delete(f"message_count:{target_user.username}")
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200
    else:
        return jsonify({'error': 'Failed to delete user'}), 500

@user_bp.route('/online', methods=['GET'])
def online_users():
    """
    Get online users.
    JSON API only - for React frontend.
    """
    if redis_service.is_available():
        users = redis_service.get_online_users()
        return jsonify({
            'success': True,
            'online_users': users,
            'count': len(users)
        }), 200
    else:
        return jsonify({
            'success': True,
            'online_users': [],
            'count': 0,
            'message': 'Redis not available'
        }), 200